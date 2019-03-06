from app import db


class FileHash(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    hash = db.Column(db.String(80))
    url = db.Column(db.String(1000))
