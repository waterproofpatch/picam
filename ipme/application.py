# standard imports
import os
import json
from datetime import datetime

# custom imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

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


class Index(Resource):
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
        print("Setting IP")

        # delete the old entry
        existing = Ip.query.first()
        if existing:
            db.session.delete(existing)

        new_ip = Ip(ip="1.2.3.4")
        db.session.add(new_ip)
        db.session.commit()


api.add_resource(Index, "/")


def init_db(db, drop_all=False):
    """
    Initialize the database.
    """
    print(f"Initializing DB {db}")
    db.init_app(application)

    if drop_all:
        print("Dropping tables...")
        db.drop_all()

    db.create_all()
    db.session.commit()


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    init_db(db, drop_all=True)

    application.debug = True
    application.run()
