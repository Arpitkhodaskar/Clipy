import redis.asyncio as redis
import json
import os
from typing import Optional, Any
import asyncio

class RedisService:
    _instance = None
    _redis = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    async def initialize(cls):
        """Initialize Redis connection"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            cls._redis = redis.from_url(redis_url, decode_responses=True)
            
            # Test the connection
            await cls._redis.ping()
            print("✅ Redis connected")
            
        except Exception as e:
            print(f"❌ Redis initialization failed: {e}")
            cls._redis = None
    
    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._redis:
            await cls._redis.close()
        print("❌ Redis disconnected")
    
    @classmethod
    async def set(cls, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis"""
        if not cls._redis:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                await cls._redis.setex(key, expire, value)
            else:
                await cls._redis.set(key, value)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        if not cls._redis:
            return None
        
        try:
            value = await cls._redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    @classmethod
    async def delete(cls, key: str) -> bool:
        """Delete a key from Redis"""
        if not cls._redis:
            return False
        
        try:
            await cls._redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    @classmethod
    async def exists(cls, key: str) -> bool:
        """Check if a key exists in Redis"""
        if not cls._redis:
            return False
        
        try:
            return await cls._redis.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False