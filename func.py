import dotenv, csv, os, json
import sqlite3 as sql
import random as rand
import pandas as pd

# Set ur own ai provider here, currently only groq is supported
from groq import Groq as ai

ranint = lambda low, high: rand.randint(low, high)
ranfloat = lambda low, high: rand.uniform(low, high)

PWD = os.getcwd()
category_config = {
    "electronics": {
        "amount": ranint(low=16, high=26),
        "loan_percentage": 0.15,
        "oddity_percentage": ranfloat(low=.14, high=.25)
    },
    "jewlery & watches": {
        "amount": ranint(low=8, high=16),
        "loan_percentage": 0.15,
        "oddity_percentage": ranfloat(low=.24, high=.46)
    },
    "firearms & sporting goods": {
        "amount": ranint(low=8, high=26),
        "loan_percentage": ranfloat(low=.15, high=.32),
        "oddity_percentage": 0.04
    },
    "home goods": {
        "amount": ranint(low=23, high=50),
        "loan_percentage": ranfloat(low=.15, high=.32),
        "oddity_percentage": 0.04
    },
    "bags and accessories": {
        "amount": ranint(low=20, high=45),
        "loan_percentage": ranfloat(low=.07, high=.24),
        "oddity_percentage": 0.04
    },
    "media": {
        "amount": ranint(low=55, high=76),
        "loan_percentage": ranfloat(low=.07, high=.08),
        "oddity_percentage": 0.24
    },
    "collectables & memorabilia": {
        "amount": ranint(low=12, high=19),
        "loan_percentage": ranfloat(low=.14, high=.25),
        "oddity_percentage": ranfloat(low=.24, high=.46)
    },
    "antiquities & art": {
        "amount": ranint(low=8, high=16),
        "loan_percentage": ranfloat(low=.14, high=.25),
        "oddity_percentage": ranfloat(low=.24, high=.46)
    },
}
category_id = {
    name: idx
    for idx, name in enumerate(category_config.keys())
}

# deco
def close_conn(func):
    def wrapper(*args, **kwargs):
        pawnshop = sql.connect(os.path.join(PWD, "database", "pawnshop.db"))
        result = func(*args, **kwargs)
        pawnshop.close()
        return result
    return wrapper


# classes for tables
class product():

    @close_conn
    def insert(item_name: str, item_id: int, price: float, quantity: int, category_id: int, item_oddities: str, colateral_id: int): 
        # product table: item_name, item_id, price, quantity, category_id, item_oddities, colateral_id
        pawnshop = sql.connect(os.path.join(PWD, "database", "pawnshop.db"))

        pawnshop.cursor().execute(f"""
        INSERT INTO products (item_name, item_id, price, quantity, category_id, item_oddities, colateral_id)
                        VALUES ("{item_name}", {item_id}, {price}, {quantity}, {category_id}, "{item_oddities}", {colateral_id})
        """)
        pawnshop.commit()
        
        return True if product.get(item_id) else False
    
    @close_conn
    def delete(item_id: int):
        pawnshop = sql.connect(os.path.join(PWD, "database", "pawnshop.db"))

        pawnshop.cursor().execute(f"DELETE FROM products WHERE item_id={item_id}")
        pawnshop.commit()

        return True if not product.get(item_id) else False

    @close_conn
    def update(item_id: int, **kwargs):
        pawnshop = sql.connect(os.path.join(PWD, "database", "pawnshop.db"))

        for key, value in kwargs.items():
            pawnshop.cursor().execute(f"UPDATE products SET {key}={value} WHERE item_id={item_id}")
        
        pawnshop.commit()

        return product.get(item_id)

    @close_conn
    def get(item_id: int):
        pawnshop = sql.connect(os.path.join(PWD, "database", "pawnshop.db"))

        return pawnshop.cursor().execute(f"SELECT * FROM products WHERE item_id={item_id}").fetchone()




# class for generated examples
class generate:

    def __init__(self, model: str = "llama-3.3-70b-versatile", env_api_key: str = "GROQ_API_KEY"):
        self.model = model
        dotenv.load_dotenv(dotenv_path=os.path.join(PWD, ".env"))

        self.Ai = ai(api_key=os.getenv(env_api_key))

        if not self.Ai: 
            comp = env_api_key.split("_")[0].upper()
            raise Exception(f"{comp} API key not found. Please set the {comp}_API_KEY environment variable.")

    def example_product(self, category: str, amount: int = 1, loan_percentage: float = 0.15, oddity_percentage: float = 0.07, start_item_id: int = 1, category_id: int = 1, dataframe: bool = True) -> pd.DataFrame | dict:
        pawnshop = sql.connect(os.path.join(PWD, "database", "pawnshop.db"))

        csv_response = self.Ai.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You are a pawnshop inventory generator. Given a product category, generate exactly {amount} realistic fake products.

                    Each product must have these fields in this exact order:
                    item_name, item_id, price, quantity, category_id, item_oddities, colateral_id

                    Rules:
                    - item_name: specific and realistic (e.g. "iPhone 13 Pro 256GB", not "cell phone")
                    - item_id: unique integer, starting at {start_item_id}, incrementing by 1
                    - price: realistic float for the category
                    - quantity: integer, rarely above 10
                    - category_id: fixed integer {category_id} for all rows in this batch
                    - item_oddities: string describing unusual traits (e.g. "vintage", "limited edition"); leave empty string "" if none — only ~{oddity_percentage*100}% of items should have one
                    - colateral_id: integer starting at 111 for loan-tied items, incrementing by 1; use null for items not tied to a loan — ~{loan_percentage*100}% of items should have one

                    You may generate multiple variants of the same product type (e.g. "iPhone 12", "iPhone 13").
                    Do not reuse products from previous prompts.
                    Return only valid CSV with a header row, no explanation, no markdown.
                    """
                },
                {
                    "role": "user",
                    "content": f"Generate {amount} products for the category of {category}."
                }
            ],
            model=self.model
        ).choices[0].message.content


        if dataframe:
            if not os.path.exists(os.path.join(PWD, "data", "example_product.csv")): 
                os.makedirs(os.path.join(PWD, "data"))
                open(os.path.join(PWD, "data", "example_product.csv"), "w").close()

            with open(os.path.join(PWD, "data", "example_product.csv"), "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["item_id", "item_name", "price", "quantity", "category_id", "item_oddities", "colateral_id"])
                reader = csv.DictReader(csv_response.splitlines())
                for product in reader:
                    try:
                        writer.writerow([
                            int(product["item_id"]),
                            str(product["item_name"]),
                            float(product["price"]),
                            int(product["quantity"]),
                            int(product["category_id"]),
                            str(product["item_oddities"]),
                            int(product["colateral_id"])])
                    except ValueError:
                        continue

            return pd.read_csv(os.path.join(PWD, "data", "example_product.csv"))
        else:
            return json.loads(csv_response)

    @close_conn
    def bulk_insert(self, dict_of_df: dict[pd.DataFrame], file_name_and_path: str, table_name: str, if_exists: str = "replace") -> bool:
        db = sql.connect(file_name_and_path)

        # combine the generated dataframes into one, sort by item_id, and save to db
        combined_df = pd.concat(dict_of_df.values(), ignore_index=True)
        ready_results = combined_df.sort_values("item_id").reset_index(drop=True)
        ready_results.sample(10)
        
        combined_df.to_sql(table_name, db, if_exists=if_exists, index=False)

        return True


if __name__ == "__main__":
    pass

    
