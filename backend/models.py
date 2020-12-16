"""
Models for the service
"""
# native imports
import json
from datetime import datetime

# third party imports
import bcrypt
from pytz import timezone

from backend import db


class JsonEncodedDict(db.TypeDecorator):
    """
    Enables JSON storage by encoding and decoding on the fly.
    """

    impl = db.Text

    def process_bind_param(self, value, dialect):
        """
        Create string from JSON dict
        """
        if value is None:
            return "{}"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        """
        Create a JSON dict from string
        """
        if value is None:
            return {}
        return json.loads(value)


class User(db.Model):
    """
    A user can log in to services
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), unique=False, nullable=False)

    def __repr__(self):
        """
        String representation for a user.
        @note don't include the password hash to prevent compromised logfiles
        from serving as a password hash dump.
        """
        return "<User {id} email={email}>".format(id=self.id, email=self.email)

    @staticmethod
    def generate_hash(plaintext_password):
        """
        Generates and returns a salted password hash
        """
        return bcrypt.hashpw(plaintext_password, bcrypt.gensalt())


class Image(db.Model):
    """
    A image contains a URL and ID.
    """

    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, unique=False, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def as_json(self):
        """
        JSON representation of this model
        """
        _created_on = timezone("US/Eastern").localize(self.created_on)
        payload = {
            "id": self.id,
            # "user_id": self.user.id, # this is sensitive, let's not reveal it
            "url": self.url,
            "created_on": _created_on.strftime("%m/%d/%y %I:%M:%S EST"),
        }

        return payload


class RevokedTokenModel(db.Model):
    """
    Store revoked tokens
    """

    __tablename__ = "revoked_tokens"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        """
        Add a token to the revoked tokens list
        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        """
        Check if a token is blacklisted
        """
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
