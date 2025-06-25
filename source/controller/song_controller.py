# controller/song_controller.py
import uuid
from redis_client.redis_client import RedisClient
from models.song import Song
from auth.auth import is_admin

class SongController:
    def __init__(self):
        self.redis = RedisClient()

    def create_song(self, user, title: str, artist: str) -> dict:
        if not is_admin(user):
            return {"success": False, "message": "Permission denied: Only admins can create songs."}

        song_id = str(uuid.uuid4())
        # key = f"song:{song_id}"
        key = f"song:{song_id}:metadata"

        self.redis.hset(key, mapping={
            "title": title,
            "artist": artist
        })
        self.redis.sadd("songs:set", song_id)
        return {"success": True, "song_id": song_id, "title": title, "artist": artist}

    def get_song(self, song_id: str) -> Song | None:
        # key = f"song:{song_id}"
        key = f"song:{song_id}:metadata"
        data = self.redis.hgetall(key)
        if not data:
            return None
        return Song(song_id=song_id, title=data.get("title"), artist=data.get("artist"))

    def list_songs(self) -> list[Song]:
        song_ids = self.redis.smembers("songs:set")
        songs = []
        for sid in song_ids:
            s = self.get_song(sid)
            if s:
                songs.append(s)
        return songs

    def update_song(self, user, song_id: str, title: str, artist: str) -> dict:
        if not is_admin(user):
            return {"success": False, "message": "Permission denied: Only admins can update songs."}

        # key = f"song:{song_id}"
        key = f"song:{song_id}:metadata"
        if not self.redis.exists(key):
            return {"success": False, "message": "Song not found."}

        self.redis.hset(key, mapping={"title": title, "artist": artist})
        return {"success": True, "message": "Song updated."}

    def delete_song(self, user, song_id: str) -> dict:
        if not is_admin(user):
            return {"success": False, "message": "Permission denied: Only admins can delete songs."}

        # key = f"song:{song_id}"
        key = f"song:{song_id}:metadata"
        if not self.redis.exists(key):
            return {"success": False, "message": "Song not found."}

        self.redis.delete(key)
        self.redis.srem("songs:set", song_id)
        self.redis.zrem("leaderboard", song_id)
        return {"success": True, "message": "Song deleted."}

    def delete_all_songs(self, user) -> dict:
        if not is_admin(user):
            return {"success": False, "message": "Permission denied."}

        song_ids = list(self.redis.smembers("songs:set"))  # cast to list to freeze members
        deleted_count = 0
        for sid in song_ids:
            self.redis.delete(f"song:{sid}")
            self.redis.zrem("leaderboard", sid)
            deleted_count += 1

        self.redis.delete("songs:set")  # clear the set after deleting members

        return {"success": True, "message": f"Deleted {deleted_count} songs.", "deleted_songs": song_ids}
