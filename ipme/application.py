# standard imports
import os
from datetime import datetime

# custom imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

# EB looks for an 'application' callable by default.
application = Flask(__name__)

db = SQLAlchemy(application)
api = Api(application)


class Ip(db.Model):
    """
    An IP address
    """

    __tablename__ = "ip"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String, unique=False, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def as_json(self):
        """
        JSON representation of this model
        """
        payload = {
            "id": self.id,
            "ip": self.ip,
        }

        return payload


def get_db_details():
    """
    Print some DB details
    """
    print(os.environ["RDS_DB_NAME"])
    print(os.environ["RDS_USERNAME"])
    # os.environ['RDS_PASSWORD'],
    print(os.environ["RDS_HOSTNAME"])
    print(os.environ["RDS_PORT"])


# print a nice greeting.
def say_hello(username="World"):
    get_db_details()
    return payload


# some bits of text for the page.
header_text = """
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>"""
instructions = """
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n"""
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = "</body>\n</html>"

# add a rule for the index page.
application.add_url_rule(
    "/", "index", (lambda: header_text + say_hello() + instructions + footer_text)
)

# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule(
    "/<username>",
    "hello",
    (lambda username: header_text + say_hello(username) + home_link + footer_text),
)


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
