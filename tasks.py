from celery import Celery
from time import sleep
from main import db
from models import FileHash
from hashlib import md5
import requests

celery = Celery(
    'tasks', 
    backend='db+sqlite:///db.sqlite',
    broker='redis://localhost:6379/0'
)

@celery.task
def download(url):
    id = celery.current_task.request.id
    file_hash = FileHash(id=id, url=url)
    db.session.add(file_hash)
    db.session.commit()

    response = requests.get(url)
    data = response.content
    file_hash.hash = md5(data).hexdigest()
    db.session.commit()

