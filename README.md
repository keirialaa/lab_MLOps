# Simple Flask App

A simple deployable Flask application with multiple routes and HTML templates.

## Routes

- `/`: Home page with HTML
- `/about`: About page
- `/cats`: Cat facts displayed in HTML
- `/dogs`: About dogs

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open http://localhost:5000 in your browser.

## Deployment

This app can be deployed to platforms like Heroku, Render, etc., that support Python apps.

For Heroku, add a `Procfile` with:
```
web: python app.py
```

## Troubleshooting

- If port 5000 is in use, change the port in app.py.