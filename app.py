from flask import Flask, request, jsonify
import mysql.connector
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# Secret key for JWT encoding/decoding
SECRET_KEY = "supersecretkey"

# Hardcoded users for this example
users = {
    "gowthami": "goproengine"
}

# ------------------------
# JWT Token Decorator
# ------------------------


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token format is invalid!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = payload['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 403

        return f(current_user, *args, **kwargs)
    return decorated

# ------------------------
# Generate JWT Token
# ------------------------


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Missing credentials'}), 401

    if users.get(auth.username) == auth.password:
        token = jwt.encode({
            'sub': auth.username,
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        }, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

# ------------------------
# Insert Data to Database
# ------------------------


def insert_sensor_data(timestamp, temperature, pressure, voltage, anomaly):
    conn = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="123456789",
            database="sensor_project"
        )

        cursor = conn.cursor()

        insert_query = """
        INSERT INTO sensor_data (timestamp, temperature, pressure, voltage, anomaly)
        VALUES (%s, %s, %s, %s, %s)
        """
        data_tuple = (timestamp, temperature, pressure, voltage, anomaly)

        cursor.execute(insert_query, data_tuple)
        conn.commit()

        return True

    except mysql.connector.Error as err:
        print(f"❌ DB Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ------------------------
# Protected Endpoint
# ------------------------


@app.route('/add_data', methods=['POST'])
@token_required
def add_data(current_user):
    try:
        data = request.get_json()
        timestamp = data.get('timestamp')
        temperature = data.get('temperature')
        pressure = data.get('pressure')
        voltage = data.get('voltage')
        anomaly = data.get('anomaly')

        if insert_sensor_data(timestamp, temperature, pressure, voltage, anomaly):
            return jsonify({"message": f"Data inserted successfully by {current_user}!"}), 201
        else:
            return jsonify({"message": "Failed to insert data!"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ------------------------
# Run App
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)
