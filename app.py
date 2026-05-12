from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='static')
CORS(app)

API_KEY = os.environ.get('GOOGLE_API_KEY', '')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/search')
def search():
    query = request.args.get('query', '')
    pagetoken = request.args.get('pagetoken', '')
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&language=pt-BR&key={API_KEY}'
    if pagetoken:
        url += f'&pagetoken={pagetoken}'
    r = requests.get(url)
    return jsonify(r.json())

@app.route('/api/details')
def details():
    place_id = request.args.get('place_id', '')
    fields = 'name,formatted_phone_number,international_phone_number,formatted_address,rating,user_ratings_total,opening_hours,website'
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&language=pt-BR&key={API_KEY}'
    r = requests.get(url)
    return jsonify(r.json())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
