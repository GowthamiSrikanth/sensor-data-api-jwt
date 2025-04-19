import requests
from requests.auth import HTTPBasicAuth

# Step 1: Get JWT token using Basic Auth (as your Flask app expects)


def get_token():
    url = "http://127.0.0.1:5000/login"
    username = "gowthami"
    password = "goproengine"

    try:
        response = requests.post(url, auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            token = response.json().get("token")
            print("✅ Token received:", token)
            return token
        else:
            print("❌ Failed to get token:", response.json())
            return None
    except Exception as e:
        print("❌ Exception occurred while getting token:", str(e))
        return None

# Step 2: Send data using the token


def add_sensor_data(token, timestamp, temperature, pressure, voltage, anomaly):
    url = "http://127.0.0.1:5000/add_data"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "timestamp": timestamp,
        "temperature": temperature,
        "pressure": pressure,
        "voltage": voltage,
        "anomaly": anomaly
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Data inserted successfully!")
        else:
            print("❌ Failed to insert data:", response.json())
    except Exception as e:
        print("❌ Exception occurred while inserting data:", str(e))


# Step 3: Run everything together
if __name__ == "__main__":
    token = get_token()
    if token:
        add_sensor_data(
            token,
            timestamp="2025-04-19 18:00:00",
            temperature=27.5,
            pressure=102.1,
            voltage=3.9,
            anomaly=False
        )
    else:
        print("⛔ Could not retrieve token. Aborting data insertion.")
