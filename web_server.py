from flask import Flask, send_file, abort
from pathlib import Path
from PIL import Image
 
app = Flask(__name__)

def find_oldest_image(directory):
    directory = Path(directory)

    # Get all files in the directory
    files = [file for file in directory.iterdir() if file.is_file()]

    # Find the newest file based on the modification time
    if files:
        oldest_file = min(files, key=lambda f: f.stat().st_mtime)
        print(f"The oldest file is: {oldest_file.name}")
    else:
        print("The directory is empty or contains no files.")

    return oldest_file


def prepare_image(image_dir):
    image = find_oldest_image(image_dir)

    image_to_send = Path('images_to_serve')  / image.name

    with Image.open(image) as img:
        img.thumbnail((1024,600))
        img.save(image_to_send)

    # delete the original image
    image.unlink()

    return image_to_send


@app.route('/download/latest_image', methods=['GET'])
def download_file():
    # Path to the directory where your binary files are stored
    image = prepare_image('downloaded_images')
    print(image)
    return send_file(image, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
