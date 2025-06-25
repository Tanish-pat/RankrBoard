import subprocess

numSongs = 100
url = "http://127.0.0.1:5000/song/create"

admin_id = "7d70364a-ad81-45cd-a50b-51ec0d467ca5"
admin_role = "ADMIN"

for i in range(1, numSongs + 1):
    title = f"song{i}"
    artist = f"artist{i}"
    payload = f'{{"title": "{title}", "artist": "{artist}"}}'

    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-H", f"X-User-Id: {admin_id}",
        "-H", f"X-User-Role: {admin_role}",
        "-d", payload
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to create {title}: {result.stderr}")
    else:
        print(f"Created {title}: {result.stdout}")
