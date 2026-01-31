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
    
    # Remove 422 Validation Error from all endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            responses = openapi_schema["paths"][path][method].get("responses", {})
            if "422" in responses:
                del responses["422"]
    
    # Remove HTTPValidationError schema if exists
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas_to_remove = ["HTTPValidationError", "ValidationError"]
        for schema in schemas_to_remove:
            if schema in openapi_schema["components"]["schemas"]:
                del openapi_schema["components"]["schemas"][schema]
    
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