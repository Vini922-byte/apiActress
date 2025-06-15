import json
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "data.db"

# Cria a tabela se não existir
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                real_name TEXT,
                birth_date TEXT,
                nationality TEXT,
                ethnicity TEXT,
                tags TEXT,
                images TEXT
            )
        ''')
        conn.commit()

init_db()

# Helper para converter registros do banco em dicionário
def row_to_dict(row):
    return {
        "id": row[0],
        "name": row[1],
        "real_name": row[2],
        "birth_date": row[3],
        "nationality": row[4],
        "ethnicity": json.loads(row[5] or "[]"),
        "tags": json.loads(row[6] or "[]"),
        "images": json.loads(row[7] or "[]")
    }

@app.route('/actresses', methods=['GET'])
def get_actresses():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actresses")
        rows = cursor.fetchall()
        return jsonify([row_to_dict(row) for row in rows])

@app.route('/actresses/<int:id>', methods=['GET'])
def get_actress(id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actresses WHERE id=?", (id,))
        row = cursor.fetchone()
        if row:
            return jsonify(row_to_dict(row))
        return jsonify({"error": "Actress not found"}), 404

@app.route('/actresses', methods=['POST'])
def create_actress():
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO actresses (name, real_name, birth_date, nationality, ethnicity, tags, images)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["name"],
            data.get("real_name"),
            data.get("birth_date"),
            data.get("nationality"),
            json.dumps(data.get("ethnicity", [])),
            json.dumps(data.get("tags", [])),
            json.dumps(data.get("images", []))
        ))
        conn.commit()
        new_id = cursor.lastrowid

    return jsonify({**data, "id": new_id}), 201

@app.route('/actresses/<int:id>', methods=['PUT'])
def update_actress(id):
    data = request.get_json()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actresses WHERE id=?", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Actress not found"}), 404

        cursor.execute('''
            UPDATE actresses
            SET name = ?, real_name = ?, birth_date = ?, nationality = ?, ethnicity = ?, tags = ?, images = ?
            WHERE id = ?
        ''', (
            data.get("name"),
            data.get("real_name"),
            data.get("birth_date"),
            data.get("nationality"),
            json.dumps(data.get("ethnicity", [])),
            json.dumps(data.get("tags", [])),
            json.dumps(data.get("images", [])),
            id
        ))
        conn.commit()

    return jsonify({"message": "Actress updated"})

@app.route('/actresses/<int:id>', methods=['DELETE'])
def delete_actress(id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actresses WHERE id=?", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Actress not found"}), 404

        cursor.execute("DELETE FROM actresses WHERE id=?", (id,))
        conn.commit()

    return jsonify({"message": "Actress deleted successfully!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
