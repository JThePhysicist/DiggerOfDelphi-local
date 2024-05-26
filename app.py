from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import json

# Load secrets from the environment file if it exists
load_dotenv('secrets.env')

#get the encryption key
key = os.getenv('ENCRYPTION_KEY')
if key is None:
    raise Exception("Encryption key not found in environment")

cipher_suite = Fernet(key.encode('utf-8'))

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///config.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define database model
class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_url = db.Column(db.String(512), nullable=False, default='https://api.example.com')
    api_key = db.Column(db.LargeBinary, nullable=False)

with app.app_context():
    db.create_all()

def encrypt_data(data):
    return cipher_suite.encrypt(data.encode('utf-8'))

def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data).decode('utf-8')

# Route to update API URL
@app.route('/update_api_url', methods=['POST'])
def update_api_url():
    try:
        #new_api_url = request.form['api_url']
        api_select = request.form['api_select']
        new_api_key = request.form['api_key']
        encrypted_api_key = encrypt_data(new_api_key)

        config = Configuration.query.first()
        if config:
            #config.api_url = new_api_url

            config.api_key = encrypted_api_key
            if api_select=='google_gemini':
                config.api_url='google_gemini'
            else:
                config.api_url=request.form['api_url']
        else:
            if api_select=='google_gemini':
                config=Configuration(api_url='google_gemini', api_key=encrypted_api_key)
            else:
                config = Configuration(api_url=request.form['api_url'], api_key = encrypted_api_key)
            db.session.add(config)
        db.session.commit()
        return 'API URL and API Key updated successfully.'
    except Exception as e:
        return str(e), 400

def call_google_gemini_api(api_key, prompt):
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-pro-vision')
    response=gemini_model.generate_content(prompt)
    return response

# Example route to use the API
@app.route('/use_api', methods=['POST'])
def use_api():
    config = Configuration.query.first()
    if not config or not config.api_key:
        return 'API Key not configured', 400

    api_key = decrypt_data(config.api_key)
    text = request.form['text']
    images=request.files.getlist('images')

    if config.api_url == 'google_gemini':
        results=[]
        for image in images:
            image_data=image.read()
            pil_image=Image.open(BytesIO(image_data))
            try:
                response = call_google_gemini_api(api_key, [text, pil_image])
                #response.resolve()
                cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
                result = json.loads(cleaned_response)
                result['image_filename'] = os.path.basename(image.filename)
                results.append(result)
            except Exception as e:
                results.append({'error':str(e), 'image_filename':  os.path.basename(image.filename)})
        #return jsonify(results)
    else:
        # Handle custom URL logic if needed
        return 'Custom URL not implemented yet', 400
    output_filename='api_results.json'
    output_path = os.path.join('output', output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_filename, 'w') as output_file:
        json.dump(results, output_file)

    return jsonify({
        'results': results,
        'download_link': f'/download/{output_filename}'
    })

# Route to download the file
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(directory=os.getcwd(), path=filename, as_attachment=True)


# Main route
@app.route('/')
def index():
    config = Configuration.query.first()
    default_api_url = config.api_url if config else 'https://api.example.com'
    return render_template('index.html', default_api_url=default_api_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
