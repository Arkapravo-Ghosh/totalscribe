"""System information routes."""

from fastapi import APIRouter
from controllers.system_controller import get_system_info

router = APIRouter()


@router.get("/system-info")
async def get_system_info_route():
    """Get system information."""
    return await get_system_info()
