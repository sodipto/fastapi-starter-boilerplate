"""
Application Resources for RBAC

Defines all available resources that permissions can be assigned to.
"""

from enum import Enum


class AppResource(str, Enum):
    """
    All available resources in the application.
    
    Each resource represents an entity or feature that permissions can be assigned to.
    """
    USERS = "users"
    ROLES = "roles"
    DOCUMENTS = "documents"
