"""
Utilities for creating various parts of the application.
"""
# project imports
from .utils import create_app, create_api, create_db

# define globals that will be imported from other files
app = create_app()
db = create_db(app)
api = create_api(app)
