import redis
import json
import logging
from datetime import datetime, timedelta
from app.config.config import Config

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                password=Config.REDIS_PASSWORD,
                decode_responses=True
            )
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def is_rate_limited(self, request_id, limit=5, window=60):
        """Check if request is rate limited"""
        if not self.redis_client:
            return False

        key = f"rate_limit:{request_id}"
        current = self.redis_client.get(key)
        
        if current is None:
            self.redis_client.setex(key, window, 1)
            return False
            
        current = int(current)
        if current >= limit:
            return True
            
        self.redis_client.incr(key)
        return False

    def get_cached_response(self, key):
        """Get cached response for a key"""
        if not self.redis_client:
            return None
            
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
            return None

    def set_cached_response(self, key, value, expiry=3600):
        """Cache response with expiry time"""
        if not self.redis_client:
            return
            
        try:
            self.redis_client.setex(
                key,
                expiry,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Error setting cached response: {e}")

    def clear_cache(self, pattern="*"):
        """Clear cache entries matching pattern"""
        if not self.redis_client:
            return
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_cache_stats(self):
        """Get cache statistics"""
        if not self.redis_client:
            return {}
            
        try:
            info = self.redis_client.info()
            return {
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_keys': info.get('db0', {}).get('keys', 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {} 