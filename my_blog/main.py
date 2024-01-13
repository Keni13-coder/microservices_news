from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from apps.mainapp.routes import api_router
from apps.error_handlers import exception_handlers
from core.custom_aiologger import CustomLoggingMiddleware

def create_app(debug=False):

    app = FastAPI(debug=debug, exception_handlers=exception_handlers)
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.mount('/media', StaticFiles(directory='media'), name='media')
    app.include_router(api_router)
    app.add_middleware(CustomLoggingMiddleware, app_name='my_blog')
    
    return app
