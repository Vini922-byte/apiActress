import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def load_data():
    try:
        with open("actresses.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data():
    with open("actresses.json", "w") as file:
        json.dump(actresses, file)

actresses = load_data()

@app.route('/actresses', methods=['GET'])
def get_actresses():
    return jsonify(actresses)

@app.route('/actresses/<int:id>', methods=['GET'])
def get_actress(id):
    actress = next((a for a in actresses if a['id'] == id), None)
    if actress:
        return jsonify(actress)
    else:
        return jsonify({"error": "Actress not found"}), 404

@app.route('/actresses', methods=['POST'])
def create_actress():
    data = request.get_json()

    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400
    
    new_actress = {
        "id": len(actresses) + 1,
        "name": data["name"],
        "real_name": data.get("real_name", None),
        "birth_date": data.get("birth_date", None),
        "nationality": data.get("nationality", None),
        "ethnicity": data.get("ethnicity", []),
        "tags": data.get("tags", []),
        "images": data.get("images", [])
    }

    actresses.append(new_actress)
    save_data()
    return jsonify(new_actress), 201

@app.route('/actresses/<int:id>', methods=['PUT'])
def update_actress(id):
    data = request.get_json()

    actress = next((a for a in actresses if a['id'] == id), None)
    if actress:
        actress["name"] = data.get("name", actress["name"])
        actress["real_name"] = data.get("real_name", actress["real_name"])
        actress["birth_date"] = data.get("birth_date", actress["birth_date"])
        actress["nationality"] = data.get("nationality", actress["nationality"])
        actress["ethnicity"] = data.get("ethnicity", actress["ethnicity"])
        actress["tags"] = data.get("tags", actress["tags"])
        actress["images"] = data.get("images", actress["images"])
        save_data()
        return jsonify(actress)
    else:
        return jsonify({"error": "Actress not found"}), 404

@app.route('/actresses/<int:id>', methods=['DELETE'])
def delete_actress(id):
    actress = next((a for a in actresses if a['id'] == id), None)
    if actress:
        actresses.remove(actress)
        save_data()
        return jsonify({"message": "Actress deleted successfully!"})
    else:
        return jsonify({"error": "Actress not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
