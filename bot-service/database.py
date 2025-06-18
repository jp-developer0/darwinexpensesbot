import asyncpg
from typing import Optional, Dict, Any
from datetime import datetime
from config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise

    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Telegram ID"""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                "SELECT id, telegram_id FROM users WHERE telegram_id = $1",
                telegram_id
            )
            return dict(row) if row else None

    async def create_user(self, telegram_id: str) -> Dict[str, Any]:
        """Create a new user"""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                "INSERT INTO users (telegram_id) VALUES ($1) RETURNING id, telegram_id",
                telegram_id
            )
            return dict(row)

    async def add_expense(
        self, 
        user_id: int, 
        description: str, 
        amount: float, 
        category: str
    ) -> Dict[str, Any]:
        """Add a new expense"""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                INSERT INTO expenses (user_id, description, amount, category, added_at) 
                VALUES ($1, $2, $3, $4, $5) 
                RETURNING id, user_id, description, amount, category, added_at
                """,
                user_id, description, str(amount), category, datetime.now()
            )
            return dict(row)

    async def is_user_whitelisted(self, telegram_id: str) -> bool:
        """Check if user is in the whitelist (exists in users table)"""
        user = await self.get_user_by_telegram_id(telegram_id)
        return user is not None


# Global database manager instance
db = DatabaseManager() 