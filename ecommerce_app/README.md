# E-commerce Platform

A comprehensive e-commerce platform built with Flask that includes basic CRUD operations, dynamic pricing, and advanced search functionality.

## Features

1. **Basic CRUD Operations**
   - Products
   - Categories
   - Users

2. **Dynamic Pricing**
   - Price adjustments based on user behavior
   - Session tracking for user visits

3. **Search Feature**
   - Search by product name, category, or price range
   - Auto-suggestions

## Setup and Installation

### macOS/Linux

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Initialize the database: `python init_db.py`
5. Run the application: `python app.py` or `python run.py`

### Windows

1. Clone the repository:
   ```
   git clone [repository-url]
   cd ecommerce_app
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a file named `.env` in the root directory
   - Add the following content:
     ```
     SECRET_KEY=your_secret_key_here
     DATABASE_URI=sqlite:///ecommerce.db
     ```

5. Initialize the database:
   ```
   python init_db.py
   ```

6. Run the application:
   ```
   python app.py
   ```
   or
   ```
   python run.py
   ```

7. Access the application in your browser at: `http://localhost:5000`

## Project Structure

- `app.py`: Main application file
- `models.py`: Database models
- `forms.py`: Form definitions
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS, images)
- `init_db.py`: Database initialization script
- `run.py`: Application launcher script
