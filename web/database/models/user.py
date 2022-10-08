from ..client import mongoEngine
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime
import hmac
import bcrypt
from sys import version_info

class User(mongoEngine.Document):
    meta = {"collection": "user"} # Collection name
    name = mongoEngine.StringField(required=True, min_length=3)
    username = mongoEngine.StringField(null=True, min_length=5)
    email = mongoEngine.StringField(required=True, unique=True)
    password = mongoEngine.StringField(required=True, min_length=6)
    created_at = mongoEngine.DateTimeField()
    updated_at = mongoEngine.DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        return super(User, self).save(*args, **kwargs)

    def update(self, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().update(**kwargs)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode("utf8")

    def check_password(self, password):
        pw_hash = self.password

        # Python version check.
        PY3 = version_info[0] >= 3

        # Python 3 unicode strings must be encoded as bytes before hashing.
        if PY3 and isinstance(pw_hash, str):
            pw_hash = bytes(pw_hash, "utf-8")

        if PY3 and isinstance(password, str):
           password = bytes(password, "utf-8")

        # Ignore unicode not defined error, Python 3 renamed the 'unicode' type to str, the old 'str' type been replaced by 'bytes'.
        if not PY3 and isinstance(pw_hash, unicode):
            pw_hash = pw_hash.encode("utf-8")

        if not PY3 and isinstance(password, unicode):
            password = password.encode("utf-8")

        return hmac.compare_digest(bcrypt.hashpw(password, pw_hash), pw_hash)

        # FlaskBcrypt DeprecationWarning: 'safe_str_cmp' is deprecated and will be removed in Werkzeug 2.1. Use 'hmac.compare_digest' instead.
        # return check_password_hash(self.password, password)
