# Leaderboard System

A high-concurrency, Redis-backed leaderboard and voting system for songs, built with Flask and Python. Supports user registration, admin management, song CRUD, and concurrent voting with benchmarking tools.

---

## Features

* **User Registration & Roles:** Register users as regular users or admins.
* **Song Management:** Admins can create, update, and delete songs.
* **Voting System:** Users can vote/unvote for songs; votes are tracked per user.
* **Leaderboard:** Real-time leaderboard with top songs, ranks, and scores.
* **High Concurrency:** Uses Redis connection pooling and pipelining for performance.
* **Benchmarking:** Includes a benchmarking script to simulate concurrent voting and measure performance.
* **REST API:** Exposes endpoints for all operations via Flask blueprints.

---

## Project Structure

```
leaderboard_system/
  source/
    app.py
    config/
      config.py
    controller/
      leaderboard_controller.py
      song_controller.py
    models/
      user.py
      song.py
    redis_client/
      redis_client.py
    auth/
      auth.py
      registration.py
    routes/
      userRoutes.py
      songRoutes.py
    build/
      main.py         # Benchmarking script
      logs/
        app.log
```

---

## Setup

### Prerequisites

* Python 3.8+
* Redis server (local or remote)
* pip (Python package manager)

### Install Dependencies

```sh
pip install flask redis tqdm
```

### Configure Redis

Edit [`config/config.py`](source/config/config.py) if you need to change Redis host/port/db.

Default:

```python
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
```

### Start Redis

Make sure Redis is running locally:

```sh
redis-server
```

---

## Running the Application

Start the Flask server: 

```sh
cd leaderboard_system/source
python app.py
```

The API will be available at `http://127.0.0.1:5000`.

---

## Docker Deployment (Linux)

### Build Docker Image

Ensure your project root contains a valid `Dockerfile`, then build the image:

```sh
docker build -t leaderboard-app .
```

### Run Container with Host Networking

```sh
docker run --network=host --env REDIS_HOST=127.0.0.1 leaderboard-app
```

> `--network=host`: Grants direct access to host network (Linux-only).
>
> `REDIS_HOST=127.0.0.1`: Ensures the container connects to Redis running on the host.

---

## API Endpoints

### User Endpoints

* `POST /user/register` Register a new user. **Body:** `{ "username": "alice", "role": "USER" | "ADMIN" }`

* `GET /user/users` List all non-admin users.

* `GET /user/admins` List all admin users.

* `PUT /user/update/<user_id>` Update a user (admin only).

* `DELETE /user/delete/<user_id>` Delete a user (admin only).

* `DELETE /user/delete_all` Delete all non-admin users (admin only).

* `POST /user/vote/<song_id>` Vote for a song.

* `POST /user/unvote/<song_id>` Remove vote from a song.

### Song Endpoints

* `POST /song/create` Create a new song (admin only). **Body:** `{ "title": "Song Title", "artist": "Artist Name" }`

* `GET /song/top?top_n=10` Get top N songs from the leaderboard.

* `GET /song/songs` List all songs.

* `GET /song/rank/<song_id>` Get rank of a song.

* `PUT /song/update/<song_id>` Update song details (admin only).

* `DELETE /song/delete/<song_id>` Delete a song (admin only).

* `DELETE /song/delete_all` Delete all songs (admin only).

**Authentication:** Pass `X-User-Id` and `X-User-Role` headers for endpoints requiring authentication.

---

## Benchmarking

The benchmarking script simulates concurrent voting and measures system performance.

Run the benchmark:

```sh
cd leaderboard_system/source/build
python main.py
```

* Configurable parameters: `TOTAL_ACTIONS`, `WORKER_STEPS` in [`main.py`](source/build/main.py)
* Logs are saved in [`logs/app.log`](source/build/logs/app.log)

```

---

## Code Overview

* **Redis Connection:** [`RedisClient`](source/redis_client/redis_client.py) uses a high-concurrency connection pool and pipelining for atomic operations.

* **User Model:** [`User`](source/models/user.py) with roles (`USER`, `ADMIN`).

* **Song Model:** [`Song`](source/models/song.py) with title and artist.

* **Controllers:**

  * [`LeaderboardController`](source/controller/leaderboard_controller.py): Voting logic, leaderboard queries.
  * [`SongController`](source/controller/song_controller.py): Song CRUD.

* **Routes:**

  * [`userRoutes`](source/routes/userRoutes.py): User and voting endpoints.
  * [`songRoutes`](source/routes/songRoutes.py): Song and leaderboard endpoints.

* **Auth:** [`auth.py`](source/auth/auth.py) and [`registration.py`](source/auth/registration.py) handle user registration, role checks, and permissions.

---

## Development & Testing

* Use tools like Postman or curl to interact with the API.
* For high-concurrency/load testing, use the provided benchmark script.
* Logs are written to [`logs/app.log`](source/build/logs/app.log).

---