# routes/songRoutes.py
from flask import Blueprint, jsonify, request, Response
import json
from collections import OrderedDict
from controller.leaderboard_controller import LeaderboardController
from controller.song_controller import SongController
from models.user import Role, User
from auth.auth import is_admin

song_routes = Blueprint('song_routes', __name__)
leaderboard_ctrl = LeaderboardController()
song_ctrl = SongController()

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

@song_routes.route('/create', methods=['POST'])
def create_song():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Unauthorized."}), 401

    data = request.json
    title = data.get('title')
    artist = data.get('artist')
    if not title or not artist:
        return jsonify({"success": False, "message": "Title and artist required."}), 400

    result = song_ctrl.create_song(user, title, artist)
    status_code = 201 if result.get("success") else 403
    return jsonify(result), status_code

@song_routes.route('/top', methods=['GET'])
def get_top_songs():
    try:
        top_n = int(request.args.get('top_n', 10))
    except ValueError:
        top_n = 10
    result = leaderboard_ctrl.top_songs(top_n)
    return jsonify(result)

@song_routes.route('/songs', methods=['GET'])
def list_songs():
    result = song_ctrl.list_songs()
    total_songs = len(result)
    song_ids = [song.song_id for song in result]
    ordered_payload = dict()
    ordered_payload["total_songs"] = total_songs
    ordered_payload["song_ids"] = song_ids
    return Response(json.dumps(ordered_payload), mimetype='application/json')

@song_routes.route('/rank/<song_id>', methods=['GET'])
def get_song_rank(song_id):
    result = leaderboard_ctrl.song_rank(song_id)
    return jsonify(result)

@song_routes.route('/update/<song_id>', methods=['PUT'])
def update_song(song_id):
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.json
    title = data.get('title')
    artist = data.get('artist')
    result = song_ctrl.update_song(user, song_id, title, artist)
    return jsonify(result), (200 if result["success"] else 403)

@song_routes.route('/delete/<song_id>', methods=['DELETE'])
def delete_song(song_id):
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    result = song_ctrl.delete_song(user, song_id)
    return jsonify(result), (200 if result["success"] else 403)

@song_routes.route('/delete_all', methods=['DELETE'])
def delete_all_songs():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    result = song_ctrl.delete_all_songs(user)
    return jsonify(result), (200 if result["success"] else 403)

