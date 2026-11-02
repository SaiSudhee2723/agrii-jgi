import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.schemas.community import (
    PostCreate,
    PostResponse,
    CommentCreate,
    CommentResponse
)
from app.core.supabase import get_supabase_client
from app.core.database import get_sqlite_conn

logger = logging.getLogger("geosense.community")

class CommunityService:
    """Module 6: Real Farmer Community discussions, comments, and authentic interactions."""

    @classmethod
    async def list_posts(
        cls,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        current_user_id: Optional[str] = None
    ) -> List[PostResponse]:
        supabase = get_supabase_client()
        if supabase:
            try:
                query = supabase.table("community_posts").select("*, profiles(full_name, avatar_url)")
                if category and category != "all":
                    query = query.eq("category", category)
                if search_query:
                    query = query.ilike("title", f"%{search_query}%")
                res = query.order("created_at", desc=True).limit(50).execute()
                posts = []
                for row in res.data:
                    profile = row.get("profiles") or {}
                    posts.append(PostResponse(
                        id=str(row["id"]),
                        user_id=str(row["user_id"]),
                        author_name=profile.get("full_name", "Farmer Member"),
                        author_avatar=profile.get("avatar_url"),
                        title=row["title"],
                        content=row["content"],
                        category=row["category"],
                        image_url=row.get("image_url"),
                        likes_count=row.get("likes_count", 0),
                        comments_count=row.get("comments_count", 0),
                        has_liked=False,
                        created_at=row["created_at"]
                    ))
                return posts
            except Exception as e:
                logger.warning(f"Supabase community query failed: {e}. Checking local database.")

        # Local database query (zero mock data: returns empty list if no user has posted)
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        sql = "SELECT * FROM community_posts WHERE 1=1"
        params = []

        if category and category != "all":
            sql += " AND category = ?"
            params.append(category)
        if search_query:
            sql += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        sql += " ORDER BY created_at DESC LIMIT 50"
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            has_liked = False
            if current_user_id:
                cursor.execute("SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?", (current_user_id, r["id"]))
                has_liked = cursor.fetchone() is not None

            results.append(PostResponse(
                id=r["id"],
                user_id=r["user_id"],
                author_name=r["author_name"],
                author_avatar=r["author_avatar"],
                title=r["title"],
                content=r["content"],
                category=r["category"],
                image_url=r["image_url"],
                likes_count=r["likes_count"],
                comments_count=r["comments_count"],
                has_liked=has_liked,
                created_at=r["created_at"]
            ))

        conn.close()
        return results

    @classmethod
    async def create_post(cls, post_in: PostCreate, user_id: str, author_name: str) -> PostResponse:
        supabase = get_supabase_client()
        now_str = datetime.utcnow().isoformat() + "Z"
        post_id = str(uuid.uuid4())

        if supabase:
            try:
                insert_data = {
                    "user_id": user_id,
                    "title": post_in.title,
                    "content": post_in.content,
                    "category": post_in.category,
                    "image_url": post_in.image_url
                }
                res = supabase.table("community_posts").insert(insert_data).execute()
                if res.data:
                    row = res.data[0]
                    return PostResponse(
                        id=str(row["id"]),
                        user_id=user_id,
                        author_name=author_name,
                        title=row["title"],
                        content=row["content"],
                        category=row["category"],
                        image_url=row.get("image_url"),
                        likes_count=0,
                        comments_count=0,
                        has_liked=False,
                        created_at=row["created_at"]
                    )
            except Exception as e:
                logger.warning(f"Could not persist post to Supabase: {e}. Storing in local database.")

        # Persist to local database
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO community_posts (id, user_id, author_name, author_avatar, title, content, category, image_url, likes_count, comments_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
        """, (post_id, user_id, author_name, "", post_in.title, post_in.content, post_in.category, post_in.image_url, now_str, now_str))
        conn.commit()
        conn.close()

        return PostResponse(
            id=post_id,
            user_id=user_id,
            author_name=author_name,
            author_avatar="",
            title=post_in.title,
            content=post_in.content,
            category=post_in.category,
            image_url=post_in.image_url,
            likes_count=0,
            comments_count=0,
            has_liked=False,
            created_at=now_str
        )

    @classmethod
    async def toggle_like(cls, post_id: str, user_id: str) -> Dict[str, Any]:
        conn = get_sqlite_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("DELETE FROM post_likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
            cursor.execute("UPDATE community_posts SET likes_count = MAX(0, likes_count - 1) WHERE id = ?", (post_id,))
            has_liked = False
        else:
            now_str = datetime.utcnow().isoformat() + "Z"
            cursor.execute("INSERT OR IGNORE INTO post_likes (user_id, post_id, created_at) VALUES (?, ?, ?)", (user_id, post_id, now_str))
            cursor.execute("UPDATE community_posts SET likes_count = likes_count + 1 WHERE id = ?", (post_id,))
            has_liked = True

        cursor.execute("SELECT likes_count FROM community_posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        likes_count = row["likes_count"] if row else 0

        conn.commit()
        conn.close()

        return {
            "post_id": post_id,
            "has_liked": has_liked,
            "likes_count": likes_count
        }

    @classmethod
    async def get_comments(cls, post_id: str) -> List[CommentResponse]:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM community_comments WHERE post_id = ? ORDER BY created_at ASC", (post_id,))
        rows = cursor.fetchall()
        conn.close()

        return [
            CommentResponse(
                id=r["id"],
                post_id=r["post_id"],
                user_id=r["user_id"],
                author_name=r["author_name"],
                author_avatar=r["author_avatar"],
                content=r["content"],
                created_at=r["created_at"]
            )
            for r in rows
        ]

    @classmethod
    async def add_comment(cls, post_id: str, comment_in: CommentCreate, user_id: str, author_name: str) -> CommentResponse:
        comment_id = str(uuid.uuid4())
        now_str = datetime.utcnow().isoformat() + "Z"

        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO community_comments (id, post_id, user_id, author_name, author_avatar, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (comment_id, post_id, user_id, author_name, "", comment_in.content, now_str))
        cursor.execute("UPDATE community_posts SET comments_count = comments_count + 1 WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()

        return CommentResponse(
            id=comment_id,
            post_id=post_id,
            user_id=user_id,
            author_name=author_name,
            author_avatar="",
            content=comment_in.content,
            created_at=now_str
        )
