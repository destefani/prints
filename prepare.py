import os
from pathlib import Path
from re import T
import tempfile
import cv2 as cv
from tqdm import tqdm


# Parameters
ORIGINAL_IMAGES_DIR = "data/png"
PROCESSED_IMAGES_DIR = "data/processed/png"
SAVE_FORMAT = "png"
TEMP = False
IMAGE_SIZE = (1748, 2480) # A5 300 dpi
INTERPOLATION = cv.INTER_AREA
ROTATION =  cv.ROTATE_90_COUNTERCLOCKWISE

#------------------------------------------------------------------------
# I/O

def load_image(image_path: str):
    try:
        if image_path.endswith((".png", ".jpg", ".jpeg")):
            img = cv.imread(image_path)
            return img
        else:
            print("Skipped:", image_path)
    except:
        print("Skipped:", image_path)


def save_image(image, save_path):
    cv.imwrite(save_path, image)

class WrongFormat(Exception):
    def __init__(self, error):
        self.error = error

#------------------------------------------------------------------------
# Transforms

def resize_image(image, size=IMAGE_SIZE, interpolation=INTERPOLATION):
    return cv.resize(image, size, interpolation)

def rotate_image(image, rotation=ROTATION):
    return cv.rotate(image, rotation)

def concatenate_images(image_1, image_2):
    image_1 = cv.imread(image_1)
    image_2 = cv.imread(image_2)
    return cv.vconcat([image_1, image_2])

def preprocessing(images_directory, temp=True):
    print("Preparing Images...")
    if temp:
        working_dir = tempfile.TemporaryDirectory()
    else:
        working_dir = Path("data/output")
    print("Files directory:", working_dir)
    for file in tqdm(os.listdir(images_directory)):
        try:
            img = load_image(images_directory + "/" + file)
            resized_img = resize_image(img)
            rotated_img = rotate_image(resized_img)
            filename = working_dir/file
            filename = str(filename).replace(" ", "")
            save_image(rotated_img, filename)
        except:
            print("Skipped:", file)

    return working_dir


def create_pages(images_directory, save_directory, save_format):
    print("Creating pages...")
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    images_directory = Path(images_directory)
    save_directory = Path(save_directory)
    files_list = os.listdir(images_directory)
    if len(files_list) % 2:
        split_on = int(len(files_list))
    else:
        split_on = int((len(files_list) - 1) / 2)

    print("Split:", split_on)

    files_list_a = files_list[:split_on]
    files_list_b = files_list[split_on:(len(files_list) - 2)]
    print(len(files_list_a))
    print(len(files_list_b))

    assert len(files_list_a) == len(files_list_b)

    for index in tqdm(range(split_on)):
        image_a = str(images_directory/files_list_a[index])
        image_b = str(images_directory/files_list_b[index])
        concatenated_images = concatenate_images(
            image_a,
            image_b
        )
        filename = f"{save_directory/str(index)}.{save_format}"
        save_image(concatenated_images, filename)

def main(files_directory, save_directory, save_format, temp):
    working_directory = preprocessing(files_directory, temp=temp)
    create_pages(working_directory, save_directory, save_format)
    if TEMP:
        working_directory.cleanup()
    

if __name__ == "__main__":
    main(ORIGINAL_IMAGES_DIR, PROCESSED_IMAGES_DIR,  SAVE_FORMAT, TEMP)



