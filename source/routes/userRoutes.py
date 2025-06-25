# routes/userRoutes.py
from flask import Blueprint, request, jsonify
from models.user import User, Role
from controller.leaderboard_controller import LeaderboardController
from auth.registration import UserRegistration

user_routes = Blueprint('user_routes', __name__)
leaderboard_ctrl = LeaderboardController()
user_reg = UserRegistration()

def is_admin(user: User) -> bool:
    return user.role == Role.ADMIN

# Mock authentication (headers)
def get_current_user():
    user_id = request.headers.get('X-User-Id')
    role_str = request.headers.get('X-User-Role')
    if not user_id or not role_str:
        return None
    try:
        role = Role(role_str)
    except ValueError:
        return None
    return User(user_id=user_id, username="mockuser", role=role)

@user_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    role_str = data.get('role', 'USER')
    try:
        role = Role(role_str)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid role."}), 400

    user = user_reg.register_user(username, role)
    return jsonify({
        "success": True,
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role.value
    }), 201

@user_routes.route('/users', methods=['GET'])
def get_all_users():
    users = user_reg.get_all_non_admin_users()
    # users_data = [{"user_id": u.user_id, "username": u.username} for u in users]
    # return jsonify({"success": True, "users": users_data})
    user_ids = [u.user_id for u in users]
    return jsonify({
        "success": True,
        "user_ids": user_ids
    })

@user_routes.route('/admins', methods=['GET'])
def get_all_admins():
    admins = user_reg.get_all_admin_users()
    admins_data = [{"user_id": a.user_id, "username": a.username} for a in admins]
    return jsonify({"success": True, "admins": admins_data})

@user_routes.route('/vote/<song_id>', methods=['POST'])
def vote(song_id):
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Unauthorized."}), 401
    result = leaderboard_ctrl.vote(user, song_id)
    return jsonify(result)

@user_routes.route('/unvote/<song_id>', methods=['POST'])
def unvote(song_id):
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Unauthorized."}), 401
    result = leaderboard_ctrl.unvote(user, song_id)
    return jsonify(result)

@user_routes.route('/update/<target_user_id>', methods=['PUT'])
def update_user(target_user_id):
    admin_user = get_current_user()
    if not admin_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.json
    username = data.get("username")
    role = data.get("role")
    result = user_reg.update_user(admin_user, target_user_id, username, role)
    return jsonify(result), (200 if result["success"] else 403)

@user_routes.route('/delete/<target_user_id>', methods=['DELETE'])
def delete_user(target_user_id):
    admin_user = get_current_user()
    if not admin_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    result = user_reg.delete_user(admin_user, target_user_id)
    return jsonify(result), (200 if result["success"] else 403)


@user_routes.route('/delete_all', methods=['DELETE'])
def delete_all_users_route():
    user = get_current_user()  # retrieve from headers/session
    if not user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    result = user_reg.delete_all_users(user)  # call service method
    status_code = 200 if result["success"] else 403
    return jsonify(result), status_code

