import requests
import random
import time
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Config
TOTAL_ACTIONS = 10000
WORKER_STEPS = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
BASE_URL = "http://127.0.0.1:5000"

# Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Shared state
votes_map = {}
votes_lock = threading.Lock()
latencies = []
lat_lock = threading.Lock()

success_counter = 0
fail_counter = 0
error_counter = 0
counter_lock = threading.Lock()

def get_all_users():
    try:
        response = requests.get(f"{BASE_URL}/user/users", timeout=10)
        response.raise_for_status()
        return response.json().get("user_ids", [])
    except Exception as e:
        logging.error(f"Failed to fetch users: {e}")
        return []

def get_all_songs():
    try:
        response = requests.get(f"{BASE_URL}/song/songs", timeout=10)
        response.raise_for_status()
        return response.json().get("song_ids", [])
    except Exception as e:
        logging.error(f"Failed to fetch songs: {e}")
        return []

def vote(song_id, user_id, vote_action=True):
    global success_counter, fail_counter, error_counter

    endpoint = "vote" if vote_action else "unvote"
    url = f"{BASE_URL}/user/{endpoint}/{song_id}"
    headers = {
        "X-User-Id": user_id,
        "X-User-Role": "USER"
    }

    start = time.time()
    try:
        response = requests.post(url, headers=headers, timeout=10)
        elapsed = time.time() - start

        with lat_lock:
            latencies.append(elapsed)

        if response.status_code in [200, 201]:
            with counter_lock:
                success_counter += 1
            return True
        else:
            with counter_lock:
                fail_counter += 1
            logging.error(f"Failed {endpoint} ({user_id} -> {song_id}): {response.status_code} - {response.text}")
            return False
    except Exception as e:
        elapsed = time.time() - start
        with counter_lock:
            error_counter += 1
        with lat_lock:
            latencies.append(elapsed)
        logging.error(f"Exception during {endpoint} ({user_id} -> {song_id}): {e}")
        return False

def simulate_votes(users, songs, total_actions, max_workers):
    def attempt_action():
        while True:
            user = random.choice(users)
            with votes_lock:
                voted = votes_map.get(user, set())

            if random.choice([True, False]):
                options = list(set(songs) - voted)
                if not options:
                    continue
                song = random.choice(options)
                if vote(song, user, True):
                    with votes_lock:
                        votes_map.setdefault(user, set()).add(song)
                break
            else:
                if not voted:
                    continue
                song = random.choice(list(voted))
                if vote(song, user, False):
                    with votes_lock:
                        votes_map[user].remove(song)
                break

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(attempt_action) for _ in range(total_actions)]
        for _ in tqdm(as_completed(futures), total=total_actions, unit="action"):
            pass

def benchmark_scaling(users, songs, step_list):
    global success_counter, fail_counter, error_counter, latencies
    for workers in step_list:
        print(f"\n--- Benchmark: {workers} workers ---")
        logging.info(f"--- Starting benchmark with {workers} workers ---")

        success_counter = fail_counter = error_counter = 0
        latencies.clear()

        start = time.time()
        simulate_votes(users, songs, TOTAL_ACTIONS, workers)
        elapsed = time.time() - start

        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        p95_lat = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0

        print(f"Time: {elapsed:.2f}s | Success: {success_counter} | Fail: {fail_counter} | Errors: {error_counter}")
        print(f"Avg Latency: {avg_lat:.3f}s | P95 Latency: {p95_lat:.3f}s")
        logging.info(f"Completed in {elapsed:.2f}s | Avg: {avg_lat:.3f}s | P95: {p95_lat:.3f}s")

def main():
    logging.info("Benchmark started")
    users = get_all_users()
    songs = get_all_songs()
    print(f"Fetched {len(users)} users and {len(songs)} songs.")
    if not users or not songs:
        print("Insufficient users or songs.")
        return
    benchmark_scaling(users, songs, WORKER_STEPS)

if __name__ == "__main__":
    main()
