import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Configurações do Flask e do banco de dados
app = Flask(__name__)
CORS(app)

# Usando a URL do banco PostgreSQL fornecida como variável de ambiente pelo Render
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # A URL do banco de dados PostgreSQL

# Inicializando o banco de dados com SQLAlchemy
db = SQLAlchemy(app)

# Definição do Modelo de Dados para 'Actress'
class Actress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    real_name = db.Column(db.String(100))
    birth_date = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    ethnicity = db.Column(db.String(100))  # Vamos armazenar como uma string JSON
    tags = db.Column(db.String(100))
    images = db.Column(db.String(100))

    def __repr__(self):
        return f'<Actress {self.name}>'

    # Método para converter os dados em dicionário (para resposta JSON)
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "real_name": self.real_name,
            "birth_date": self.birth_date,
            "nationality": self.nationality,
            "ethnicity": json.loads(self.ethnicity or "[]"),
            "tags": json.loads(self.tags or "[]"),
            "images": json.loads(self.images or "[]")
        }

# Criando as tabelas no banco de dados
@app.before_request
def create_tables():
    db.create_all()

# Rotas da API
@app.route('/actresses', methods=['GET'])
def get_actresses():
    actresses = Actress.query.all()
    return jsonify([actress.as_dict() for actress in actresses])

@app.route('/actresses/<int:id>', methods=['GET'])
def get_actress(id):
    actress = Actress.query.get(id)
    if actress:
        return jsonify(actress.as_dict())
    return jsonify({"error": "Actress not found"}), 404

@app.route('/actresses', methods=['POST'])
def create_actress():
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    new_actress = Actress(
        name=data["name"],
        real_name=data.get("real_name"),
        birth_date=data.get("birth_date"),
        nationality=data.get("nationality"),
        ethnicity=json.dumps(data.get("ethnicity", [])),
        tags=json.dumps(data.get("tags", [])),
        images=json.dumps(data.get("images", []))
    )

    db.session.add(new_actress)
    db.session.commit()

    return jsonify(new_actress.as_dict()), 201

@app.route('/actresses/<int:id>', methods=['PUT'])
def update_actress(id):
    data = request.get_json()
    actress = Actress.query.get(id)

    if not actress:
        return jsonify({"error": "Actress not found"}), 404

    actress.name = data.get("name", actress.name)
    actress.real_name = data.get("real_name", actress.real_name)
    actress.birth_date = data.get("birth_date", actress.birth_date)
    actress.nationality = data.get("nationality", actress.nationality)
    actress.ethnicity = json.dumps(data.get("ethnicity", []))
    actress.tags = json.dumps(data.get("tags", []))
    actress.images = json.dumps(data.get("images", []))

    db.session.commit()

    return jsonify(actress.as_dict())

@app.route('/actresses/<int:id>', methods=['DELETE'])
def delete_actress(id):
    actress = Actress.query.get(id)
    if not actress:
        return jsonify({"error": "Actress not found"}), 404

    db.session.delete(actress)
    db.session.commit()

    return jsonify({"message": "Actress deleted successfully!"})

@app.route('/import-json', methods=['POST'])
def import_json():
    try:
        with open("actresses.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for actress in data:
            new_actress = Actress(
                id=actress.get("id"),
                name=actress.get("name"),
                real_name=actress.get("real_name"),
                birth_date=actress.get("birth_date"),
                nationality=actress.get("nationality"),
                ethnicity=json.dumps(actress.get("ethnicity", [])),
                tags=json.dumps(actress.get("tags", [])),
                images=json.dumps(actress.get("images", []))
            )
            db.session.add(new_actress)

        db.session.commit()
        return jsonify({"message": f"{len(data)} actresses imported successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Executando a aplicação
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

""" import json
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
CORS(app)

DB_PATH = "data.db"


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Usando a URL fornecida pelo Render

db = SQLAlchemy(app)
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


@app.route('/import-json', methods=['POST'])
def import_json():
    try:
        with open("actresses.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            for actress in data:
                cursor.execute('''
                    INSERT INTO actresses (id, name, real_name, birth_date, nationality, ethnicity, tags, images)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    actress.get("id"),
                    actress.get("name"),
                    actress.get("real_name"),
                    actress.get("birth_date"),
                    actress.get("nationality"),
                    json.dumps(actress.get("ethnicity", [])),
                    json.dumps(actress.get("tags", [])),
                    json.dumps(actress.get("images", []))
                ))
            conn.commit()

        return jsonify({"message": f"{len(data)} atrizes importadas com sucesso."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
   """  
    
    
""" import json
from flask import Flask, jsonify, request
from flask_cors import CORS

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
    app.run(port=5000, debug=True)
 """
