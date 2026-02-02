"""
Application Actions for RBAC

Defines all available actions that can be performed on resources.
"""

from enum import Enum


class AppAction(str, Enum):
    """
    All available actions in the application.
    
    Each action represents an operation that can be performed on a resource.
    """
    VIEW = "view"
    SEARCH = "search"
    CREATE = "create"
    UPDATE = "update"
    UPSERT = "upsert"
    DELETE = "delete"
    EXECUTE = "execute"
    GENERATE = "generate"
    CLEAN = "clean"
    EXPORT = "export"
    IMPORT = "import"
    UPLOAD = "upload"
