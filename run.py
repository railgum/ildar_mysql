from app import app
from dotenv import load_dotenv
import os


load_dotenv()

from functions import path_to_save_images, make_dir  # noqa


if __name__ == '__main__':

    make_dir(path_to_save_images, f"{os.environ.get('SLIDER')}")
    make_dir(path_to_save_images, f"{os.environ.get('MINICARD')}")
    make_dir(path_to_save_images, f"{os.environ.get('FEATURETTE')}")
    make_dir(path_to_save_images, f"{os.environ.get('FOOTER')}")

    app.run()
