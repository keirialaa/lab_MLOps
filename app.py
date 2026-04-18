from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cats')
def cats():
    cat_facts = [
        "Cats have over 20 muscles that control their ears.",
        "A group of cats is called a clowder.",
        "Cats sleep for around 13 to 16 hours a day.",
        "Cats have five toes on their front paws, but only four on the back paws."
    ]
    return render_template('cats.html', facts=cat_facts)

@app.route('/dogs')
def dogs():
    return render_template('dogs.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)