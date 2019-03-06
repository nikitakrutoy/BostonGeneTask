from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import request
import tasks
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

from models import *
db.create_all()

@app.route("/submit", methods=["post"])
def submit():
    url = request.form["url"]
    task = tasks.download.delay(url)
    return jsonify(dict(id=task.id))

@app.route("/check", methods=["get"])
def check():
    id = request.args.get("id")
    state = tasks.celery.AsyncResult(id).state
    if state == "SUCCESS":
        filehash = FileHash.query.get(id)
        return jsonify(
            {
                "id": id,
                "status": state,
                "md5": filehash.hash,
                "url": filehash.url,
            }
        )
    if state == "FAILURE":
        return jsonify(
            {
                "status": state,
                "error": "Probably wrong url :)",
            }
        )        
    else:
        return jsonify(
            {
                "status": "running",
            }
        )   


if __name__ == "__main__":
    app.run()