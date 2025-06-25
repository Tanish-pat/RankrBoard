from enum import Enum

class Role(Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User:
    def __init__(self, user_id: str, username: str, role: Role):
        self.user_id = user_id
        self.username = username
        self.role = role

    def __repr__(self):
        return f"<User id={self.user_id} username={self.username} role={self.role.value}>"
