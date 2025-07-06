# Taxi Booking System

A simple Taxi Booking System web application built with Python Flask for a student project.

## Project Overview

This application provides a platform for taxi booking with separate portals for drivers and customers, including a driver recommendation engine.

### Features

- **Basic CRUD Operations** for Drivers, Customers, and Rides
- **Driver Portal**:
  - View total earnings from completed rides
  - Access ride summaries, including customer ratings and feedback
- **Customer Portal**:
  - Book a ride with pickup and drop-off locations
  - Choose from available drivers
  - Make dummy payments
  - Leave ratings and feedback for drivers
- **Driver Recommendation System** based on:
  - Customer ratings
  - Proximity to pickup location
  - Number of rides completed

## Setup Instructions

### Prerequisites

- Python 3.7+
- SQLite

### Installation

1. Clone or download this repository to your local machine

2. Navigate to the project directory:
```
cd taxiapp
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Run the application:
```
python app.py
```

5. Open your web browser and go to:
```
http://localhost:5000
```

## Usage

### For Customers:

1. Register or log in as a customer
2. Book a ride by specifying pickup and drop-off locations
3. Select a driver from the recommendations
4. Complete the ride when finished
5. Make a payment (dummy process)
6. Rate the driver and provide feedback

### For Drivers:

1. Register or log in as a driver
2. Update your availability status and location
3. View earnings, ratings, and ride history

## Database Structure

The application uses SQLite with the following tables:
- Drivers
- Customers
- Rides

## Note

This is a simplified student project and doesn't include real payment processing or actual geolocation services. The location data is simulated for educational purposes.
