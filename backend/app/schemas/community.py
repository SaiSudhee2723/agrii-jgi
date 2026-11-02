from typing import List, Optional
from pydantic import BaseModel, Field

class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    author_name: str
    author_avatar: Optional[str] = None
    content: str
    created_at: str

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=5, max_length=5000)
    category: str = Field(default="general")
    image_url: Optional[str] = None

class PostResponse(BaseModel):
    id: str
    user_id: str
    author_name: str
    author_avatar: Optional[str] = None
    title: str
    content: str
    category: str
    image_url: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    has_liked: bool = False
    created_at: str

class DirectMessageCreate(BaseModel):
    receiver_id: str
    content: str = Field(..., min_length=1, max_length=2000)

class DirectMessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    sender_name: Optional[str] = None
    content: str
    is_read: bool
    created_at: str

