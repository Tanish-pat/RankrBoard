# controller/leaderboard_controller.py
from auth.auth import can_vote
from leaderboard import Leaderboard
from models.user import User

class LeaderboardController:
    def __init__(self):
        self.leaderboard = Leaderboard()

    def vote(self, user: User, song_id: str) -> dict:
        if not can_vote(user):
            return {"success": False, "message": "Permission denied: Cannot vote."}
        success = self.leaderboard.vote_song(user.user_id, song_id)
        if not success:
            return {"success": False, "message": "Already voted for this song."}
        return {"success": True, "message": "Vote registered."}

    def unvote(self, user: User, song_id: str) -> dict:
        if not can_vote(user):
            return {"success": False, "message": "Permission denied: Cannot unvote."}
        success = self.leaderboard.unvote_song(user.user_id, song_id)
        if not success:
            return {"success": False, "message": "You have not voted for this song."}
        return {"success": True, "message": "Vote removed."}

    def top_songs(self, top_n: int = 10) -> dict:
        results = self.leaderboard.get_top_songs(top_n)
        return {"success": True, "data": results}

    def song_rank(self, song_id: str) -> dict:
        rank = self.leaderboard.get_song_rank(song_id)
        if rank is None:
            return {"success": False, "message": "Song not ranked."}
        return {"success": True, "rank": rank}
