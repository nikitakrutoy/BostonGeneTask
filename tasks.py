from celery import Celery
from time import sleep
from app import db
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
    # sleep(100)
    response = requests.get(url)
    data = response.content
    id = celery.current_task.request.id
    hash = md5(data).hexdigest()
    file_hash = FileHash(id=id, hash=hash, url=url)
    db.session.add(file_hash)
    db.session.commit()
