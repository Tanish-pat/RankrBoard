# app.py
from flask import Flask
from routes.userRoutes import user_routes
from routes.songRoutes import song_routes

app = Flask(__name__)

# Register blueprints
app.register_blueprint(user_routes, url_prefix='/user')
app.register_blueprint(song_routes, url_prefix='/song')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
