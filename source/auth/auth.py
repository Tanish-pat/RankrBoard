# auth/auth.py
from models.user import Role, User
from auth.registration import UserRegistration

def is_admin(user: User) -> bool:
    return user.role == Role.ADMIN

def can_vote(user: User) -> bool:
    # Both USER and ADMIN can vote
    return user.role in {Role.USER, Role.ADMIN}

def can_manage(user: User) -> bool:
    # Only ADMIN can perform management tasks (e.g., adding songs)
    return user.role == Role.ADMIN

user_reg = UserRegistration()
def is_registered(user_id: str) -> bool:
    return user_reg.user_exists(user_id)
