# standard imports
import re

# installed imports
from flask_restful import Resource
from flask import request

# project imports
from src import app, db
from src.models import Ip

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