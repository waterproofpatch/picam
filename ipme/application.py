# standard imports
import re
import os
from datetime import datetime

# custom imports
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

app = Flask(__name__)

db = SQLAlchemy(app)
api = Api(app)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]


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
            # "created_on": self.created_on.strftime("%m/%d/%y %I:%M:%S"),
        }

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
        ip = Ip.query.first().as_json()["ip"]
        last_updated = "Not Implemented"  # ip.as_ison()["last_updated"]
        return f'<center><div style="font-size: 20px"><a href="https://{ip}:4443">Camera</a><br>Updated on {last_updated}</div><center>'
    else:
        return '<center><div style="font-size: 20px">No IP reported.</div></center>'


def init_db(db, drop_all=False):
    """
    Initialize the database.
    """
    print(f"Initializing DB {db}")
    db.init_app(app)

    if drop_all:
        print("Dropping tables...")
        db.drop_all()

    db.create_all()
    db.session.commit()


api.add_resource(IpEndpoint, "/ip")
init_db(db, drop_all=True)

# run the app.
if __name__ == "__main__":
    app.debug = True
    app.run(port=5001)
