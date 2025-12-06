"""
User Management API Router

Endpoints for managing users (admin only).
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any

from models.schemas import UserInfo, UserUpdate, UserListResponse
from utils.auth import require_role, hash_password
from utils.logger import logger

# Import users_db from auth router
from routers.auth import users_db

router = APIRouter()


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users",
    description="Get list of all registered users (admin only)",
)
async def list_users(current_user: Dict = Depends(require_role("admin"))):
    """
    List all users in the system

    Requires: admin role
    """
    try:
        users_list = []

        for user in users_db.values():
            users_list.append(
                UserInfo(
                    username=user["username"],
                    email=user["email"],
                    role=user["role"],
                    created_at=user.get("created_at"),
                    last_login=user.get("last_login"),
                )
            )

        logger.info(f"User list requested by admin: {current_user['username']}")

        return UserListResponse(users=users_list, count=len(users_list))

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user list")


@router.get(
    "/{username}", response_model=UserInfo, summary="Get user details", description="Get details of a specific user"
)
async def get_user(username: str, current_user: Dict = Depends(require_role("admin"))):
    """
    Get user information

    Requires: admin role
    """
    try:
        user = users_db.get(username)

        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        return UserInfo(
            username=user["username"],
            email=user["email"],
            role=user["role"],
            created_at=user.get("created_at"),
            last_login=user.get("last_login"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user information")


@router.patch(
    "/{username}", response_model=UserInfo, summary="Update user", description="Update user role or email (admin only)"
)
async def update_user(username: str, update_data: UserUpdate, current_user: Dict = Depends(require_role("admin"))):
    """
    Update user information

    Requires: admin role

    Request body:
    ```json
    {
        "role": "doctor",
        "email": "newemail@hospital.com"
    }
    ```
    """
    try:
        user = users_db.get(username)

        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        # Prevent self-demotion from admin
        if username == current_user["username"] and update_data.role and update_data.role.value != "admin":
            raise HTTPException(status_code=400, detail="Cannot change your own admin role")

        # Update fields
        if update_data.role:
            user["role"] = update_data.role.value
            logger.info(f"User role updated: {username} -> {update_data.role.value}")

        if update_data.email:
            # Check email uniqueness
            for other_username, other_user in users_db.items():
                if other_username != username and other_user["email"] == update_data.email:
                    raise HTTPException(status_code=400, detail="Email already in use")
            user["email"] = update_data.email
            logger.info(f"User email updated: {username}")

        return UserInfo(
            username=user["username"],
            email=user["email"],
            role=user["role"],
            created_at=user.get("created_at"),
            last_login=user.get("last_login"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account (admin only)",
)
async def delete_user(username: str, current_user: Dict = Depends(require_role("admin"))):
    """
    Delete a user account

    Requires: admin role

    Cannot delete your own admin account.
    """
    try:
        if username not in users_db:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        # Prevent self-deletion
        if username == current_user["username"]:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")

        del users_db[username]
        logger.info(f"User deleted by admin {current_user['username']}: {username}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Get current user",
    description="Get information about the currently authenticated user",
)
async def get_current_user_info(current_user: Dict = Depends(require_role("admin", "doctor", "nurse", "viewer"))):
    """
    Get current user information

    Requires: Any authenticated user
    """
    try:
        username = current_user["username"]
        user = users_db.get(username)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserInfo(
            username=user["username"],
            email=user["email"],
            role=user["role"],
            created_at=user.get("created_at"),
            last_login=user.get("last_login"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user information")
