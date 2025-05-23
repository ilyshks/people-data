from app import db


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    location = db.Column(db.JSON)
    photo = db.Column(db.LargeBinary)
    profile = db.Column(db.String(255))
