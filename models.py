from app import db
import base64


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    location = db.Column(db.JSON)
    photo = db.Column(db.LargeBinary)

    def photo_base64(self):
        if self.photo:
            return base64.b64encode(self.photo).decode('utf-8')
        return None
