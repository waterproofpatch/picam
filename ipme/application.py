"""
Web proxy
"""

# standard imports
import re
import os
from datetime import datetime

# installed imports
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

app = Flask(__name__)

db = SQLAlchemy(app)
api = Api(app)

INDEX_TEMPLATE = """
<center><div style="font-size: 20px">
<a href="https://{ip}:4443">
Camera
</a>
<br>
Updated on {last_updated}
</div>
<center>
"""


class Ip(db.Model):
    """
    An IP address
    """

    __tablename__ = "ip"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String, unique=False, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def as_json(self):
        """
        JSON representation of this model
        """
        payload = {"id": self.id, "ip": self.ip, "last_updated": "N/A"}

        return payload


class IpEndpoint(Resource):
    """
    Ip endpoint
    """

    def get(self):
        """
        Get the IP for the pi
        """
        print("Got a request for the IP endpoint")
        return [x.as_json() for x in Ip.query.all()]

    def post(self):
        """
        Expects a JSON payload formed:
        {"ip" "1.2.3.4"}
        """
        if "ip" not in request.get_json():
            return {"error": "invalid request"}, 400

        ip = request.get_json()["ip"]
        if not re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip):
            return {"error": "invalid request"}, 400

        print(f"Setting IP to {ip}")

        # delete the old entry
        existing = Ip.query.first()
        if existing:
            db.session.delete(existing)

        db.session.add(Ip(ip=ip))
        db.session.commit()
        return {}


@app.route("/")
def get_html():
    """
    Get an HTML page with a link to the camera.
    """
    if Ip.query.first():
        report = Ip.query.first().as_json()
        return INDEX_TEMPLATE.format(
            last_updated=report["last_updated"], ip=report["ip"]
        )
    return '<center><div style="font-size: 20px">No IP reported.</div></center>'


def init_db():
    """
    Initialize the database.
    """
    print(f"Initializing DB {db}")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

    print(f"App config: {app.config}")

    db.init_app(app)
    db.create_all()
    db.session.commit()


# add resources
api.add_resource(IpEndpoint, "/ip")

# init database
init_db()

# run the app in debug mode
if __name__ == "__main__":
    print("Running from main!")
    app.debug = True
    app.run(port=5001)
