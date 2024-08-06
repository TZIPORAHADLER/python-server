from flask import Flask, jsonify, request
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

headers = {
    'x-rapidapi-key': '911ed75ab4mshf7c8c0b2022acb4p107a7djsncaf0755c4a71',
    'x-rapidapi-host': 'house-plants2.p.rapidapi.com'
}

def get_paginated_data(data, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    return data[start:end]

@app.route('/api/categories', methods=['GET'])
def get_all_categories():
    url = "https://house-plants2.p.rapidapi.com/categories"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to retrieve categories: {str(e)}', 'status': response.status_code if response else 'N/A'}), 500

@app.route('/api/plants/category/<string:category>', methods=['GET'])
def get_plants_by_category(category):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    url = f"https://house-plants2.p.rapidapi.com/category/{category}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        paginated_data = get_paginated_data(data, page, limit)
        return jsonify(paginated_data)
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch plants by category: {str(e)}', 'status': response.status_code if response else 'N/A'}), 500

@app.route('/api/lite', methods=['GET'])
def get_all_lite():
    url = "https://house-plants2.p.rapidapi.com/all-lite"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to retrieve lites: {str(e)}', 'status': response.status_code if response else 'N/A'}), 500

@app.route('/api/id/<string:id>', methods=['GET'])
def get_by_id(id):
    url = f"https://house-plants2.p.rapidapi.com/id/{id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch plant by id: {str(e)}', 'status': response.status_code if response else 'N/A'}), 500

@app.route("/api/all", methods=["GET"])
def get_all():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    url = "https://house-plants2.p.rapidapi.com/all"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        paginated_data = get_paginated_data(data, page, limit)
        return jsonify(paginated_data)
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get all: {str(e)}', 'status': response.status_code if response else 'N/A'}), 500

@app.route('/api/search', methods=['GET'])
def search_by_query():
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    url = "https://house-plants2.p.rapidapi.com/search"
    querystring = {"query": query}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        print("Response data from RapidAPI:", data)

        filtered_data = filter_by_latin_name_or_family(data, query)
        paginated_data = get_paginated_data(filtered_data, page, limit)
        print("Filtered data:", filtered_data)
        return jsonify(paginated_data)
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to retrieve data by search: {str(e)}', 'status': response.status_code if response else 'N/A'}), 500

def filter_by_latin_name_or_family(data, query):
    filtered_data = []
    for plant in data:
        print("plant ", plant)
        item = plant.get('item', {})
        if item:
            latin_name = item.get('Latin name', '')
            family = item.get('Family', '')

            if query.lower() in latin_name.lower() or query.lower() in family.lower():
                filtered_data.append(plant)
        else:
            print("Not found")
    return filtered_data

def extract_required_fields(data):
    if isinstance(data, list):
        return [
            {
                "id": item.get("id"),
                "Latin name": item.get("Latin name"),
                "Family": item.get("Family"),
                "Categories": item.get("Categories")
            }
            for item in data
        ]

@app.route("/api/filtered", methods=["GET"])
def get_filtered_data():
    try:
        response = get_all()
        data = response.json
        filtered_data = extract_required_fields(data)
        return jsonify(filtered_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get filtered data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
