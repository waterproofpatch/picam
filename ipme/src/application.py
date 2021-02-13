"""
Web proxy
"""

# standard imports
import re
from datetime import datetime

# installed imports

# project imports
from src import app

# run the app in debug mode
if __name__ == "__main__":
    print("Running from main!")
    app.debug = True
    app.run(port=5001)
