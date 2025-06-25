# auth/registration.py
import uuid
from redis_client.redis_client import RedisClient
from models.user import Role, User

def is_admin(user: User) -> bool:
    return user.role == Role.ADMIN

class UserRegistration:
    def __init__(self):
        self.redis = RedisClient()
        self.redis.delete("leaderboard")

    def register_user(self, username: str, role: Role = Role.USER) -> User:
        user_id = str(uuid.uuid4())
        key = f"user:{user_id}"

        # Save user hash
        self.redis.hset(key, mapping={
            "username": username,
            "role": role.value
        })

        # Add to users set
        self.redis.sadd("users:set", user_id)

        return User(user_id=user_id, username=username, role=role)

    def get_all_non_admin_users(self) -> list[User]:
        # Pull only the registered user IDs
        all_ids = self.redis.smembers("users:set")
        users = []
        for user_id in all_ids:
            key = f"user:{user_id}"
            data = self.redis.hgetall(key)
            if not data:
                continue
            if data.get("role") != Role.ADMIN.value:
                users.append(User(user_id=user_id,
                                username=data.get("username", ""),
                                role=Role(data.get("role"))))
        return users

    def get_all_admin_users(self) -> list[User]:
        all_ids = self.redis.smembers("users:set")
        admins = []
        for user_id in all_ids:
            key = f"user:{user_id}"
            data = self.redis.hgetall(key)
            if data.get("role") == Role.ADMIN.value:
                admins.append(User(user_id=user_id,
                                username=data.get("username", ""),
                                role=Role(data.get("role"))))
        return admins

    def get_user(self, user_id: str) -> User | None:
        key = f"user:{user_id}"
        data = self.redis.hgetall(key)
        if not data:
            return None
        role = Role(data.get("role"))
        return User(user_id=user_id, username=data.get("username"), role=role)

    def user_exists(self, user_id: str) -> bool:
        return self.redis.exists(f"user:{user_id}") == 1

    def update_user(self, user, target_user_id: str, new_username: str, new_role: str):
        if not is_admin(user):
            return {"success": False, "message": "Permission denied: Only admins can update users."}

        key = f"user:{target_user_id}"
        if not self.redis.exists(key):
            return {"success": False, "message": "User not found."}

        self.redis.hset(key, mapping={"username": new_username, "role": new_role})
        return {"success": True, "message": "User updated."}

    def delete_user(self, user, target_user_id: str):
        if not is_admin(user):
            return {"success": False, "message": "Permission denied: Only admins can delete users."}

        key = f"user:{target_user_id}"
        if not self.redis.exists(key):
            return {"success": False, "message": "User not found."}

        self.redis.delete(key)
        return {"success": True, "message": "User deleted."}

    # def delete_all_users(self, admin_user) -> dict:
    #     if not is_admin(admin_user):
    #         return {"success": False, "message": "Permission denied: Only admins can delete all users."}

    #     user_keys = self.redis.keys("user:*")
    #     user_vote_keys = []

    #     deleted_count = 0
    #     pipe = self.redis.pipeline()

    #     for key in user_keys:
    #         role = self.redis.hget(key, "role")
    #         if role == Role.ADMIN.value:
    #             continue  # skip admins

    #         user_id = key.split(":")[1]
    #         user_vote_keys.append(f"user_votes:{user_id}")

    #         pipe.delete(key)
    #         deleted_count += 1

    #     for key in user_vote_keys:
    #         pipe.delete(key)

    #     pipe.execute()

    #     return {"success": True, "message": f"Deleted {deleted_count} users and their votes."}

    def delete_all_users(self, admin_user) -> dict:
        if not is_admin(admin_user):
            return {"success": False, "message": "Permission denied."}

        all_ids = self.redis.smembers("users:set")
        deleted = 0
        pipe = self.redis.pipeline()
        for user_id in all_ids:
            key = f"user:{user_id}"
            data = self.redis.hgetall(key)
            if data.get("role") == Role.ADMIN.value:
                continue
            pipe.delete(key)
            pipe.srem("users:set", user_id)
            pipe.delete(f"user:{user_id}:voted_songs")
            deleted += 1
        pipe.execute()

        return {"success": True, "message": f"Deleted {deleted} users and their votes."}
