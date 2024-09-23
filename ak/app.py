import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for sessions

NOMINATIM_API_URL = 'https://nominatim.openstreetmap.org/reverse'

# Predefined route for testing purposes
bus_route = [
    {'latitude': 9.3150, 'longitude': 76.6150},  # Chengannur
    {'latitude': 9.3165, 'longitude': 76.6165},
    {'latitude': 9.3180, 'longitude': 76.6180},
    {'latitude': 9.3200, 'longitude': 76.6200},
    # Add more points if necessary
    {'latitude': 9.3980, 'longitude': 76.7020}   # Mavelikara
]

# Global variables to track the bus state
current_index = 0
bus_started = False

# Function to reverse geocode coordinates into a readable address
def get_location_name(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json'
    }
    response = requests.get(NOMINATIM_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('display_name', 'Unknown Location')
    return 'Unknown Location'

@app.route('/')
def index():
    if 'role' in session:
        if session['role'] == 'driver':
            return render_template('driver.html', bus_started=bus_started)
        elif session['role'] == 'user':
            return render_template('user.html')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'admin' and password == 'admin':
        if 'driver' in request.form:
            session['role'] = 'driver'
        elif 'user' in request.form:
            session['role'] = 'user'
        return redirect(url_for('index'))
    else:
        return "Invalid credentials, try again."

@app.route('/start_bus', methods=['POST'])
def start_bus():
    global bus_started
    if session['role'] == 'driver':
        bus_started = True
        return jsonify({'message': 'Bus journey started successfully!'})
    return jsonify({'error': 'Unauthorized access'}), 403

@app.route('/stop_bus', methods=['POST'])
def stop_bus():
    global bus_started, current_index
    if session['role'] == 'driver':
        bus_started = False
        current_index = 0  # Reset the bus position
        return jsonify({'message': 'Bus journey stopped successfully!'})
    return jsonify({'error': 'Unauthorized access'}), 403

@app.route('/get_bus_location', methods=['GET'])
def get_bus_location():
    global current_index, bus_started

    if bus_started and current_index < len(bus_route):
        bus_position = bus_route[current_index]
        current_index += 1

        # Reverse geocode the location to get the place name
        place_name = get_location_name(bus_position['latitude'], bus_position['longitude'])

        return jsonify({
            'latitude': bus_position['latitude'],
            'longitude': bus_position['longitude'],
            'place_name': place_name
        })
    
    if current_index >= len(bus_route):  # Reset if the route is complete
        bus_started = False
        current_index = 0
    
    return jsonify({'error': 'Bus not started yet'}), 400

@app.route('/logout')
def logout():
    session.pop('role', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
