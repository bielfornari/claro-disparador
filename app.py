from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import time
import urllib.parse

app = Flask(__name__, static_folder='static')
CORS(app)

API_KEY = os.environ.get('GOOGLE_API_KEY', '')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# ── Busca por texto (modo segmento) ──────────────────────────────────────────
@app.route('/api/search')
def search():
    query     = request.args.get('query', '')
    pagetoken = request.args.get('pagetoken', '')
    url = (f'https://maps.googleapis.com/maps/api/place/textsearch/json'
           f'?query={urllib.parse.quote(query)}&language=pt-BR&key={API_KEY}')
    if pagetoken:
        url += f'&pagetoken={urllib.parse.quote(pagetoken)}'
    r = requests.get(url, timeout=10)
    return jsonify(r.json())

# ── Geocoding: texto → lat/lng ───────────────────────────────────────────────
@app.route('/api/geocode')
def geocode():
    address = request.args.get('address', '')
    url = (f'https://maps.googleapis.com/maps/api/geocode/json'
           f'?address={urllib.parse.quote(address)}&language=pt-BR&key={API_KEY}')
    r = requests.get(url, timeout=10)
    return jsonify(r.json())

# ── Nearby Search: qualquer negócio num raio ─────────────────────────────────
@app.route('/api/nearby')
def nearby():
    lat       = request.args.get('lat', '')
    lng       = request.args.get('lng', '')
    radius    = request.args.get('radius', '1500')
    pagetoken = request.args.get('pagetoken', '')

    if pagetoken:
        time.sleep(2)  # obrigatório pelo Google antes de usar pagetoken
        url = (f'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
               f'?pagetoken={urllib.parse.quote(pagetoken)}&key={API_KEY}')
    else:
        url = (f'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
               f'?location={lat},{lng}&radius={radius}'
               f'&type=establishment&language=pt-BR&key={API_KEY}')

    r = requests.get(url, timeout=10)
    return jsonify(r.json())

# ── Detalhes de um place ─────────────────────────────────────────────────────
@app.route('/api/details')
def details():
    place_id = request.args.get('place_id', '')
    fields   = ('name,formatted_phone_number,international_phone_number,'
                'formatted_address,rating,user_ratings_total,opening_hours,website,types')
    url = (f'https://maps.googleapis.com/maps/api/place/details/json'
           f'?place_id={urllib.parse.quote(place_id)}'
           f'&fields={fields}&language=pt-BR&key={API_KEY}')
    r = requests.get(url, timeout=10)
    return jsonify(r.json())

# ── CNPJ via ReceitaWS (proxy para evitar CORS no browser) ───────────────────
@app.route('/api/cnpj')
def cnpj():
    nome   = request.args.get('nome', '').strip()
    cidade = request.args.get('cidade', '').strip().upper()
    if not nome:
        return jsonify({'error': 'nome obrigatorio'})
    try:
        url = f'https://receitaws.com.br/v1/cnpj/search?query={urllib.parse.quote(nome)}'
        r = requests.get(url, timeout=8, headers={
            'Accept': 'application/json',
            'User-Agent': 'LeadHunter/1.0'
        })
        data = r.json()
        # Filtra pelo município se vier lista
        companies = data.get('companies', data if isinstance(data, list) else [])
        if companies:
            match = next(
                (x for x in companies if cidade in (x.get('municipio', '') or '').upper()),
                companies[0]
            )
            return jsonify(match)
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
