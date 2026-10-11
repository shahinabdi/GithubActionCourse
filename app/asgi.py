from starlette.middleware.wsgi import WSGIMiddleware

from app import create_app
from app.api import create_api_app

app = create_api_app()
app.mount("/", WSGIMiddleware(create_app()))
