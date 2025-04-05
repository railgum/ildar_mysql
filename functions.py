from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
from app import app
import os
import re


path_to_save_images = os.path.join(app.root_path, 'static', 'imgs')


# проверка расширения файла изображения
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in os.environ.get('ALLOWED_EXTENSIONS')


# Функция обработки изображения
def process_img_file(file, short_title):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(
            path_to_save_images, f'{short_title}/{filename}')
        imgpath = f'/static/imgs/{short_title}/' + filename
        file = Image.open(file)

        # Обработка загруженного файла
        if short_title == os.environ.get('SLIDER'):
            file = ImageOps.fit(file, tuple_from_str(os.environ.get('MAX_SIZE_SLIDER')),
                                centering=(0.5, 0.5))
        elif short_title == os.environ.get('MINICARD'):
            file = ImageOps.fit(
                file, tuple_from_str(os.environ.get('MAX_SIZE_MINICARD')), centering=(0.5, 0.5))
        elif short_title == os.environ.get('FEATURETTE'):
            file = ImageOps.fit(file, tuple_from_str(os.environ.get('MAX_SIZE_FEATURETTE')),
                                centering=(0.5, 0.5))
        file.save(save_path)
        return imgpath
    else:
        return None


# Функция создания папки для статики
def make_dir(path, folder_name):
    path = os.path.join(path, folder_name)
    if path != None:
        if not os.path.exists(path):
            os.mkdir(path)


# кортеж размеров картинки для Image.ops
def tuple_from_str(str_ex):
    nums = re.findall(r'\d+', str_ex)
    return tuple([int(i) for i in nums])
