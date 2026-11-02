import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.community import (
    PostCreate,
    PostResponse,
    CommentCreate,
    CommentResponse
)
from app.services.community_service import CommunityService
from app.core.security import get_current_user_optional, get_current_user_required

logger = logging.getLogger("geosense.api.community")
router = APIRouter()

@router.get("/posts", response_model=List[PostResponse], summary="Fetch community discussion feed")
async def get_posts(
    category: Optional[str] = Query(None, description="Category filter (soil_health, pest_control, crop_advice, market, general)"),
    search: Optional[str] = Query(None, description="Keyword search query"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """Module 6: Community feed with category filtering and keyword search."""
    user_id = current_user.get("sub") if current_user else None
    return await CommunityService.list_posts(category=category, search_query=search, current_user_id=user_id)

@router.post("/posts", response_model=PostResponse, summary="Create a new community post")
async def create_post(
    post_in: PostCreate,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Allows authenticated farmers to publish a discussion post."""
    user_id = current_user.get("sub", "anonymous-farmer")
    author_name = current_user.get("user_metadata", {}).get("full_name") or current_user.get("email", "Farmer Member")
    return await CommunityService.create_post(post_in, user_id=user_id, author_name=author_name)

@router.post("/posts/{post_id}/like", summary="Toggle like on a community post")
async def toggle_like(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Likes or unlikes a post for the authenticated user."""
    user_id = current_user.get("sub", "anon")
    return await CommunityService.toggle_like(post_id, user_id)

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse], summary="Get comment thread for a post")
async def get_comments(post_id: str):
    return await CommunityService.get_comments(post_id)

@router.post("/posts/{post_id}/comments", response_model=CommentResponse, summary="Add a comment to a post")
async def add_comment(
    post_id: str,
    comment_in: CommentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    user_id = current_user.get("sub", "anonymous-farmer")
    author_name = current_user.get("user_metadata", {}).get("full_name") or current_user.get("email", "Farmer Member")
    return await CommunityService.add_comment(post_id, comment_in, user_id=user_id, author_name=author_name)

