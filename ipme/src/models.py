from datetime import datetime

from src import db


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
        payload = {
            "id": self.id,
            "ip": self.ip,
            "last_updated": self.last_updated.ctime(),
        }

        return payload


db.create_all()