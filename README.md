# Voleibol_upravlenie_turnorom

This Flask application manages a beach volleyball tournament. Teams of two or three players compete in knockout brackets for multiple categories.

## Local development

```bash
pip install -r requirements.txt
python app.py
```
The application listens on the port defined by the `PORT` environment variable (default `8080`).

## Deploying to Railway

1. Connect this repository to Railway.
2. Set the start command to `python app.py` (a `Procfile` is included).
3. Railway automatically sets the `PORT` environment variable (typically `8080`).
4. After deployment, open the provided Railway URL to manage your tournament.
