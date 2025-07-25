from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from app.core.jwt_security import JWTBearer

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Input your Bearer token to access all endpoints"
        }
    }
    
    # Apply to all routes globally (optional)
    for route in app.routes:
            if isinstance(route, APIRoute):
                for dep in route.dependant.dependencies:
                    if (
                        isinstance(dep.call, type(JWTBearer())) or
                        isinstance(dep.call, JWTBearer)
                    ):
                        path = route.path
                        methods = route.methods
                        for method in methods:
                            method = method.lower()
                            if path in openapi_schema["paths"]:
                                if method in openapi_schema["paths"][path]:
                                    openapi_schema["paths"][path][method]["security"] = [{"Bearer": []}]
            
    app.openapi_schema = openapi_schema
    return app.openapi_schema