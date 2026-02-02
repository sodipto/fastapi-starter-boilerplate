"""
Claim Types for RBAC

Defines claim type constants and enums used in the permission system.
"""

from enum import Enum


class AppClaim:
    """Claim type constants."""
    PERMISSION = "permission"
    ROLE = "role"
    SCOPE = "scope"


class PermissionClaimType(str, Enum):
    """
    Claim types used in RoleClaim tables.
    
    This defines the 'claim_type' field value for permission claims.
    """
    PERMISSION = "permission"           # Standard permission claim
    ROLE = "role"                       # Role membership claim
    SCOPE = "scope"                     # OAuth scope claim
