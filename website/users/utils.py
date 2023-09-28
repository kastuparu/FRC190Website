import secrets
import os
from PIL import Image

from website import app


def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(4)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    resized_picture = Image.open(form_picture)
    resized_picture.thumbnail((500, 500))
    resized_picture.save(picture_path)
    return picture_filename
