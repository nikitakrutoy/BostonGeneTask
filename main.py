from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__, static_url_path="", static_folder="doc", template_folder="doc")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['STATIC_FOLDER'] = "./doc"
db = SQLAlchemy(app)

import tasks

from models import *
db.create_all()




"""
@api {POST} /submit Submit file to download
@apiName Submit
@apiGroup FileHashing
@apiParam {Number} url File url.
@apiSuccess {String} id Unique submit id.
@apiSuccessExample Success:
    HTTP/1.1 200 OK
    {
      "id": "0e4fac17-f367-4807-8c28-8a059a2f82ac",
    }
@apiExample {curl} Example Usage:
    curl -X POST -d "email=user@example.com&url=http://site.com/file.txt" https://nikitakrutoy.ml/bostongene-task/submit
"""
@app.route("/submit", methods=["post"])
def submit():
    url = request.form["url"]
    task = tasks.download.delay(url)
    return jsonify(dict(id=task.id))



"""
@api {GET} /check Check file status
@apiName Check
@apiGroup FileHashing
@apiParam {Number} id Unique submit id.
@apiSuccess {String} md5 md5 file hash.
@apiSuccess {String} url File url.
@apiSuccess {String} status Submit status.
@apiSuccessExample Success:
    HTTP/1.1 200 OK
    {
        "md5":"f4afe93ad799484b1d512cc20e93efd1",
        "status":"SUCCESS",
        "url": "http://site.com/file.txt"
    }
@apiSuccessExample Running:
    HTTP/1.1 200 OK
    {
        "status":"RUNNING",
    }
@apiSuccessExample Failed:
    HTTP/1.1 200 OK
    {
        "status":"FAILED",
        "error": "Probably wrong url :("
    }
@apiError (Error404) SubmitNotFound The <code>id</code> of the Submit was not found.
@apiExample {curl} Example Usage:
    curl -X GET https://nikitakrutoy.ml/bostongene-task/check?id=0e4fac17-f367-4807-8c28-8a059a2f82ac
"""
@app.route("/check", methods=["get"])
def check():
    id = request.args.get("id", None)
    filehash = FileHash.query.get_or_404(id)
    state = tasks.celery.AsyncResult(id).state
    if state == "SUCCESS":
        return jsonify(
            {
                "status": state,
                "md5": filehash.hash,
                "url": filehash.url,
            }
        )
    elif state == "FAILURE":
        return jsonify(
            {
                "status": state,
                "error": "Probably wrong url :(",
            }
        )        
    else:
        return jsonify(
            {
                "status": "RUNNING",
            }
        )   

@app.route("/", methods=["get"])
def home():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run()