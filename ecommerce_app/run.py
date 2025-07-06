#!/usr/bin/env python
# Helps run the application from the command line

from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
