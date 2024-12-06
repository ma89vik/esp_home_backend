from flask import Flask, send_file, abort, request, jsonify
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import os
from functools import wraps
from tinydb import TinyDB, Query

load_dotenv()
API_KEY = os.getenv('PHOTOS_API_KEY')
assert API_KEY is not None

app = Flask(__name__)
serve_dir = Path('images_to_serve')
db = TinyDB('db.json')

def require_api_key(f):
    """Decorator to require an API key for a route."""
    @wraps(f) # Preserve the original function's name and metadata
    def decorated_function(*args, **kwargs):
        # Look for the API key in headers or query parameters
        key = request.headers.get("x-api-key") or request.args.get("api_key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function



def prepare_images(image_dir):
    directory = Path(image_dir)


    # Get all files in the directory
    for file in directory.iterdir():
        if not file.is_file():
            continue

        image_to_send = serve_dir / file.name

        with Image.open(file) as img:
            img.thumbnail((1024,600))
            img.save(image_to_send)

        # delete the original image
        file.unlink()
        db.insert({'name': file.name, 'served': False})

    images = [file.name for file in serve_dir.iterdir() if file.is_file()]
    return images


@app.route('/get_image_list', methods=['GET'])
@require_api_key
def get_image_list():
    # Path to the directory where your binary files are stored
    images = prepare_images('downloaded_images')
    print(f'Available images {images}')

    return jsonify(images)

@app.route('/download/<filename>', methods=['GET'])
@require_api_key
def download_image(filename):
    try:
        # Construct the file path
        file_path = serve_dir / filename

        # Serve the file
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        # If the file does not exist, return a 404 error
        abort(404, description="File not found")

@app.route('/download/latest_image', methods=['GET'])
@require_api_key
def download_latest_image():
    prepare_images('downloaded_images')
    # Construct the file path
    image = Query()

    unserved = db.search(image.served == False)
    print(unserved)

    # Serve the file
    if unserved:
        return send_file(serve_dir / unserved[0]['name'], as_attachment=True)
    else:
        return '', 204

@app.route('/tag/<filename>', methods=['post'])
@require_api_key
def tag_file_server(filename):
    # Construct the file path
    image = Query()
    db.update({'served': True}, image.name == filename)
    return '', 200
