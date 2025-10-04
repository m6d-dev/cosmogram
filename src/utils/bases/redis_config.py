from redis import Redis
from typing import Union
import redis
import os


class RedisConfig:
    def get_redis(self) -> Union[Redis, bool]:
        rd = Redis(
            host=os.environ.get("REDIS_HOST"),
            port=os.environ.get("REDIS_PORT"),
            decode_responses=True,
            health_check_interval=30,
        )
        if not self.check_health(redis_conn=rd):
            return False
        return rd

    def check_health(self, redis_conn: Redis):
        try:
            redis_conn.ping()
            return True
        except redis.ConnectionError:
            return False
