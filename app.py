from flask import Flask, request, jsonify, render_template
import requests
import io
import importlib

app = Flask(__name__)

def install_package(package):
    try:
        importlib.import_module(package)
    except ImportError:
        import subprocess
        subprocess.call(['pip', 'install', package])


@app.route('/')
def home():
    return render_template('index.html')
       
        
        
@app.route('/remove-background', methods=['GET'])
def remove_background():
    try:
        import rembg
    except ImportError:
        install_package('rembg')
        import rembg

    try:
        import PIL
    except ImportError:
        install_package('Pillow')
        import PIL

    from PIL import Image

    
    image_url = request.args.get('image')
    image = requests.get(f"https://{image_url}").content

    try:
        output = rembg.remove(image)
        output_image = Image.open(io.BytesIO(output))
        cropped_image = output_image.crop(output_image.getbbox())  # Crop to the maximum extent
        cropped_image_bytes = io.BytesIO()
        cropped_image.save(cropped_image_bytes, format='PNG')
        cropped_image_bytes.seek(0)
    except Exception as e:
        return jsonify({'error': str(e)})

    return jsonify({'result': cropped_image_bytes.getvalue()})

if __name__ == '__main__':
    try:
        import flask
    except ImportError:
        install_package('flask')
        import flask

    app.run(host='0.0.0.0', port=8080)
