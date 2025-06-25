# leaderboard.py
from redis_client.redis_client import RedisClient, retry_redis_call
from auth.registration import UserRegistration
from models.song import Song

user_reg = UserRegistration()

class Leaderboard:
    LEADERBOARD_KEY = "songs:leaderboard"
    USER_VOTES_KEY_PATTERN = "user:{user_id}:voted_songs"

    def __init__(self):
        self.redis = RedisClient()

    def vote_song(self, user_id: str, song_id: str) -> bool:
        if not user_reg.user_exists(user_id):
            return False
        user_votes_key = self.USER_VOTES_KEY_PATTERN.format(user_id=user_id)
        if self.redis.sismember(user_votes_key, song_id):
            return False
        # self.redis.sadd(user_votes_key, song_id)
        # self.redis.zincrby(self.LEADERBOARD_KEY, 1, song_id)
        # EXTRA #
        pipe = self.redis.pipeline()
        pipe.sadd(user_votes_key, song_id)
        pipe.zincrby(self.LEADERBOARD_KEY, 1, song_id)
        pipe.execute()
        # EXTRA #

        return True

    def unvote_song(self, user_id: str, song_id: str) -> bool:
        user_votes_key = self.USER_VOTES_KEY_PATTERN.format(user_id=user_id)
        if not self.redis.sismember(user_votes_key, song_id):
            return False
        # self.redis.srem(user_votes_key, song_id)
        # EXTRA #
        pipe = self.redis.pipeline()
        pipe.srem(user_votes_key, song_id)
        # EXTRA #

        current_score = self.redis.zscore(self.LEADERBOARD_KEY, song_id)
        if current_score is None or current_score <= 1:
            # self.redis.zrem(self.LEADERBOARD_KEY, song_id)
            # EXTRA #
            pipe.zrem(self.LEADERBOARD_KEY, song_id)
            # EXTRA #
        else:
            # self.redis.zincrby(self.LEADERBOARD_KEY, -1, song_id)
            # EXTRA #
            pipe.zincrby(self.LEADERBOARD_KEY, -1, song_id)
            # EXTRA #
        pipe.execute()
        return True

    # def get_top_songs(self, top_n: int = 10) -> list:
    #     return self.redis.zrevrange(self.LEADERBOARD_KEY, 0, top_n - 1, withscores=True)

    # def get_song_rank(self, song_id: str) -> int:
    #     rank = self.redis.zrevrank(self.LEADERBOARD_KEY, song_id)
    #     return rank + 1 if rank is not None else None

    # def get_song_score(self, song_id: str) -> int:
    #     score = self.redis.zscore(self.LEADERBOARD_KEY, song_id)
    #     return int(score) if score is not None else 0

    def get_top_songs(self, top_n: int = 10) -> list:
        """
        Return list of dicts: {song_id, score, title, artist}
        """
        top_songs = retry_redis_call(
            self.redis.zrevrange,
            self.LEADERBOARD_KEY,
            0,
            top_n - 1,
            withscores=True
        )

        pipe = self.redis.pipeline()
        for song_id, _ in top_songs:
            meta_key = f"song:{song_id}:metadata"
            pipe.hget(meta_key, "title")
            pipe.hget(meta_key, "artist")

        metadata = pipe.execute()

        results = []
        for i, (song_id, score) in enumerate(top_songs):
            title = metadata[2*i] or "Unknown Title"
            artist = metadata[2*i + 1] or "Unknown Artist"
            results.append({
                "song_id": song_id,
                "score": score,
                "title": title,
                "artist": artist
            })
        return results


    def get_song_rank(self, song_id: str) -> int:
        rank = retry_redis_call(
            self.redis.zrevrank,
            self.LEADERBOARD_KEY,
            song_id
        )
        return rank + 1 if rank is not None else None

    def get_song_score(self, song_id: str) -> int:
        score = retry_redis_call(
            self.redis.zscore,
            self.LEADERBOARD_KEY,
            song_id
        )
        return int(score) if score is not None else 0