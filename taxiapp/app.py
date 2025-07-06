from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import math
import os

app = Flask(__name__)
app.secret_key = 'taxi_booking_secret_key'

# Database initialization
def init_db():
    conn = sqlite3.connect('taxi_booking.db')
    cursor = conn.cursor()
    
    # Create drivers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        vehicle_number TEXT NOT NULL,
        vehicle_model TEXT NOT NULL,
        location_lat REAL DEFAULT 0,
        location_lng REAL DEFAULT 0,
        is_available BOOLEAN DEFAULT 1,
        avg_rating REAL DEFAULT 0,
        total_rides INTEGER DEFAULT 0
    )
    ''')
    
    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create rides table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        driver_id INTEGER NOT NULL,
        pickup_location TEXT NOT NULL,
        dropoff_location TEXT NOT NULL,
        pickup_lat REAL NOT NULL,
        pickup_lng REAL NOT NULL,
        dropoff_lat REAL NOT NULL,
        dropoff_lng REAL NOT NULL,
        ride_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        amount REAL DEFAULT 0,
        rating INTEGER DEFAULT 0,
        feedback TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (driver_id) REFERENCES drivers (id)
    )
    ''')
    
    # Insert sample drivers data (simple numbered names)
    sample_drivers = [
        ('Driver1', '9876543210', 'driver1@example.com', 'password123', 'TN01AB1234', 'Toyota Innova', 12.9716, 77.5946, 1, 4.5, 15),
        ('Driver2', '8765432109', 'driver2@example.com', 'password123', 'TN02CD5678', 'Honda City', 12.9352, 77.6245, 1, 4.8, 20),
        ('Driver3', '7654321098', 'driver3@example.com', 'password123', 'TN03EF9012', 'Hyundai i20', 12.9592, 77.6974, 1, 4.2, 8),
        ('Driver4', '6543210987', 'driver4@example.com', 'password123', 'TN04GH3456', 'Maruti Swift', 13.0298, 77.5763, 1, 4.6, 12),
        ('Driver5', '5432109876', 'driver5@example.com', 'password123', 'TN05IJ7890', 'Tata Nexon', 12.9791, 77.6408, 1, 4.3, 10)
    ]
    
    # Check if drivers table is empty before inserting sample data
    cursor.execute('SELECT COUNT(*) FROM drivers')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO drivers (name, phone, email, password, vehicle_number, vehicle_model, 
                            location_lat, location_lng, is_available, avg_rating, total_rides)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_drivers)
    
    # Insert sample customers data (simple numbered names)
    sample_customers = [
        ('Customer1', '9876543211', 'customer1@example.com', 'password123'),
        ('Customer2', '8765432100', 'customer2@example.com', 'password123'),
        ('Customer3', '7654321099', 'customer3@example.com', 'password123'),
        ('Customer4', '6543210988', 'customer4@example.com', 'password123'),
        ('Customer5', '5432109877', 'customer5@example.com', 'password123')
    ]
    
    # Check if customers table is empty before inserting sample data
    cursor.execute('SELECT COUNT(*) FROM customers')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO customers (name, phone, email, password)
        VALUES (?, ?, ?, ?)
        ''', sample_customers)
    
    conn.commit()
    conn.close()

# Initialize database on startup
if not os.path.exists('taxi_booking.db'):
    # Create new database if it doesn't exist
    init_db()

# Calculate distance between two points (using Haversine formula)
def calculate_distance(lat1, lng1, lat2, lng2):
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lng1 = math.radians(lng1)
    lat2 = math.radians(lat2)
    lng2 = math.radians(lng2)
    
    # Haversine formula
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

# Calculate ride fare based on distance
def calculate_fare(distance):
    base_fare = 50  # Base fare in INR
    per_km_rate = 10  # Per kilometer rate in INR
    
    # Ensure distance is reasonable (limit to 1000km to prevent extreme values)
    capped_distance = min(distance, 1000)
    
    # Round to 2 decimal places to avoid floating point issues
    fare = base_fare + (capped_distance * per_km_rate)
    return round(fare, 2)

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Registration and login routes
@app.route('/register/<user_type>', methods=['GET', 'POST'])
def register(user_type):
    if request.method == 'POST':
        conn = sqlite3.connect('taxi_booking.db')
        cursor = conn.cursor()
        
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        
        if user_type == 'driver':
            vehicle_number = request.form['vehicle_number']
            vehicle_model = request.form['vehicle_model']
            
            cursor.execute('''
            INSERT INTO drivers (name, phone, email, password, vehicle_number, vehicle_model)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, password, vehicle_number, vehicle_model))
        else:
            cursor.execute('''
            INSERT INTO customers (name, phone, email, password)
            VALUES (?, ?, ?, ?)
            ''', (name, phone, email, password))
        
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login', user_type=user_type))
        
    return render_template(f'{user_type}_register.html')

@app.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type):
    if request.method == 'POST':
        conn = sqlite3.connect('taxi_booking.db')
        cursor = conn.cursor()
        
        email = request.form['email']
        password = request.form['password']
        
        if user_type == 'driver':
            cursor.execute('SELECT * FROM drivers WHERE email = ? AND password = ?', (email, password))
        else:
            cursor.execute('SELECT * FROM customers WHERE email = ? AND password = ?', (email, password))
            
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['user_type'] = user_type
            session['user_id'] = user[0]
            session['name'] = user[1]
            
            if user_type == 'driver':
                return redirect(url_for('driver_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid login credentials', 'danger')
            
    return render_template(f'{user_type}_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Customer routes
@app.route('/customer/dashboard')
def customer_dashboard():
    if session.get('logged_in') and session.get('user_type') == 'customer':
        conn = sqlite3.connect('taxi_booking.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fetch customer's ride history
        cursor.execute('''
        SELECT r.*, d.name as driver_name, d.vehicle_number, d.vehicle_model
        FROM rides r
        JOIN drivers d ON r.driver_id = d.id
        WHERE r.customer_id = ?
        ORDER BY r.ride_date DESC
        ''', (session['user_id'],))
        
        rides = cursor.fetchall()
        conn.close()
        
        return render_template('customer_dashboard.html', rides=rides)
    return redirect(url_for('login', user_type='customer'))

@app.route('/customer/book-ride', methods=['GET', 'POST'])
def book_ride():
    if not (session.get('logged_in') and session.get('user_type') == 'customer'):
        return redirect(url_for('login', user_type='customer'))
    
    if request.method == 'POST':
        pickup_location = request.form['pickup_location']
        dropoff_location = request.form['dropoff_location']
        
        # Handle potential empty values with validation and defaults
        try:
            pickup_lat = float(request.form['pickup_lat']) if request.form['pickup_lat'] else 0.0
            pickup_lng = float(request.form['pickup_lng']) if request.form['pickup_lng'] else 0.0
            dropoff_lat = float(request.form['dropoff_lat']) if request.form['dropoff_lat'] else 0.0
            dropoff_lng = float(request.form['dropoff_lng']) if request.form['dropoff_lng'] else 0.0
            driver_id = int(request.form['driver_id'])
        except ValueError:
            flash('Invalid location data. Please try again.', 'danger')
            return redirect(url_for('book_ride'))
        
        distance = calculate_distance(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
        fare = calculate_fare(distance)
        
        conn = sqlite3.connect('taxi_booking.db')
        cursor = conn.cursor()
        
        # Create a new ride
        cursor.execute('''
        INSERT INTO rides (customer_id, driver_id, pickup_location, dropoff_location, 
                          pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], driver_id, pickup_location, dropoff_location, 
              pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, fare))
        
        ride_id = cursor.lastrowid
        
        # Update driver availability
        cursor.execute('UPDATE drivers SET is_available = 0 WHERE id = ?', (driver_id,))
        
        conn.commit()
        conn.close()
        
        flash('Ride booked successfully!', 'success')
        return redirect(url_for('view_ride', ride_id=ride_id))
    
    # Get available drivers for recommendation
    conn = sqlite3.connect('taxi_booking.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM drivers
    WHERE is_available = 1
    ORDER BY avg_rating DESC, total_rides DESC
    ''')
    
    available_drivers = cursor.fetchall()
    conn.close()
    
    return render_template('book_ride.html', available_drivers=available_drivers)

@app.route('/ride/<int:ride_id>')
def view_ride(ride_id):
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    conn = sqlite3.connect('taxi_booking.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT r.*, c.name as customer_name, d.name as driver_name, 
           d.vehicle_number, d.vehicle_model, d.phone as driver_phone
    FROM rides r
    JOIN customers c ON r.customer_id = c.id
    JOIN drivers d ON r.driver_id = d.id
    WHERE r.id = ?
    ''', (ride_id,))
    
    ride = cursor.fetchone()
    conn.close()
    
    if not ride:
        flash('Ride not found', 'danger')
        return redirect(url_for('home'))
    
    # Check if the user is authorized to view this ride
    if (session['user_type'] == 'customer' and ride['customer_id'] != session['user_id']) or \
       (session['user_type'] == 'driver' and ride['driver_id'] != session['user_id']):
        flash('You are not authorized to view this ride', 'danger')
        return redirect(url_for('home'))
    
    return render_template('view_ride.html', ride=ride)

@app.route('/customer/complete-ride/<int:ride_id>', methods=['POST'])
def complete_ride_customer(ride_id):
    if not (session.get('logged_in') and session.get('user_type') == 'customer'):
        return redirect(url_for('login', user_type='customer'))
    
    conn = sqlite3.connect('taxi_booking.db')
    cursor = conn.cursor()
    
    # Update ride status
    cursor.execute('UPDATE rides SET status = ? WHERE id = ?', ('completed', ride_id))
    
    conn.commit()
    conn.close()
    
    flash('Ride completed! Please make payment and rate your driver.', 'success')
    return redirect(url_for('payment', ride_id=ride_id))

@app.route('/customer/payment/<int:ride_id>', methods=['GET', 'POST'])
def payment(ride_id):
    if not (session.get('logged_in') and session.get('user_type') == 'customer'):
        return redirect(url_for('login', user_type='customer'))
    
    conn = sqlite3.connect('taxi_booking.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM rides WHERE id = ?', (ride_id,))
    ride = cursor.fetchone()
    
    if request.method == 'POST':
        # This is a dummy payment process
        cursor.execute('UPDATE rides SET status = ? WHERE id = ?', ('paid', ride_id))
        conn.commit()
        
        flash('Payment successful!', 'success')
        return redirect(url_for('rate_driver', ride_id=ride_id))
    
    conn.close()
    return render_template('payment.html', ride=ride)

@app.route('/customer/rate/<int:ride_id>', methods=['GET', 'POST'])
def rate_driver(ride_id):
    if not (session.get('logged_in') and session.get('user_type') == 'customer'):
        return redirect(url_for('login', user_type='customer'))
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        feedback = request.form['feedback']
        
        conn = sqlite3.connect('taxi_booking.db')
        cursor = conn.cursor()
        
        # Update ride with rating and feedback
        cursor.execute('UPDATE rides SET rating = ?, feedback = ? WHERE id = ?', 
                      (rating, feedback, ride_id))
        
        # Get the driver id for this ride
        cursor.execute('SELECT driver_id FROM rides WHERE id = ?', (ride_id,))
        driver_id = cursor.fetchone()[0]
        
        # Update driver's average rating
        cursor.execute('''
        UPDATE drivers 
        SET avg_rating = (SELECT AVG(rating) FROM rides WHERE driver_id = ? AND rating > 0),
            total_rides = total_rides + 1,
            is_available = 1
        WHERE id = ?
        ''', (driver_id, driver_id))
        
        conn.commit()
        conn.close()
        
        flash('Thank you for your rating and feedback!', 'success')
        return redirect(url_for('customer_dashboard'))
    
    conn = sqlite3.connect('taxi_booking.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT r.*, d.name as driver_name 
    FROM rides r 
    JOIN drivers d ON r.driver_id = d.id 
    WHERE r.id = ?
    ''', (ride_id,))
    
    ride = cursor.fetchone()
    conn.close()
    
    return render_template('rate_driver.html', ride=ride)

# Driver routes
@app.route('/driver/dashboard')
def driver_dashboard():
    if session.get('logged_in') and session.get('user_type') == 'driver':
        conn = sqlite3.connect('taxi_booking.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fetch driver info
        cursor.execute('SELECT * FROM drivers WHERE id = ?', (session['user_id'],))
        driver = cursor.fetchone()
        
        # Fetch completed rides
        cursor.execute('''
        SELECT r.*, c.name as customer_name 
        FROM rides r
        JOIN customers c ON r.customer_id = c.id
        WHERE r.driver_id = ?
        ORDER BY r.ride_date DESC
        ''', (session['user_id'],))
        
        rides = cursor.fetchall()
        
        # Calculate total earnings
        cursor.execute('SELECT SUM(amount) FROM rides WHERE driver_id = ? AND status = ?', 
                      (session['user_id'], 'paid'))
        
        total_earnings = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return render_template('driver_dashboard.html', driver=driver, rides=rides, total_earnings=total_earnings)
    
    return redirect(url_for('login', user_type='driver'))

@app.route('/driver/update-location', methods=['POST'])
def update_location():
    if not (session.get('logged_in') and session.get('user_type') == 'driver'):
        return redirect(url_for('login', user_type='driver'))
    
    lat = float(request.form['lat'])
    lng = float(request.form['lng'])
    
    conn = sqlite3.connect('taxi_booking.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE drivers SET location_lat = ?, location_lng = ? WHERE id = ?',
                  (lat, lng, session['user_id']))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('driver_dashboard'))

@app.route('/driver/toggle-availability', methods=['POST'])
def toggle_availability():
    if not (session.get('logged_in') and session.get('user_type') == 'driver'):
        return redirect(url_for('login', user_type='driver'))
    
    conn = sqlite3.connect('taxi_booking.db')
    cursor = conn.cursor()
    
    # Get current availability
    cursor.execute('SELECT is_available FROM drivers WHERE id = ?', (session['user_id'],))
    current_status = cursor.fetchone()[0]
    
    # Toggle availability
    new_status = 0 if current_status else 1
    cursor.execute('UPDATE drivers SET is_available = ? WHERE id = ?',
                  (new_status, session['user_id']))
    
    conn.commit()
    conn.close()
    
    status_text = "available" if new_status else "unavailable"
    flash(f'You are now {status_text} for new rides', 'success')
    return redirect(url_for('driver_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
