import subprocess

numUsers = 10000
url = "http://127.0.0.1:5000/user/register"

for i in range(1, numUsers + 1):
    username = f"user{i}"
    payload = f'{{"username": "{username}", "role": "USER"}}'
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", payload
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to register {username}: {result.stderr}")
    else:
        print(f"Registered {username}: {result.stdout}")
