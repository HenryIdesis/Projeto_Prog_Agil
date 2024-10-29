from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from auth import requires_auth, hash_password, init_mongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@progeficaz.yni5x.mongodb.net/projeto"
mongo = PyMongo(app)


init_mongo(mongo)

def create_admin_user():
    if mongo.db.cadastro.find_one({"usuario": "admin"}) is None:
        user_data = {"nome": "Admin", "usuario": "admin", "senha": generate_password_hash("admin123"), "email": "admin@example.com"}
        mongo.db.cadastro.insert_one(user_data)
        print("Usuário admin criado com sucesso!")
    else:
        print("Usuário admin já existe.")

create_admin_user()

@app.route('/cadastro', methods=['POST'])
def create_user():
    """Rota para criar um novo usuário."""
    nome = request.json.get('nome')
    usuario = request.json.get('usuario')
    senha = request.json.get('senha')
    email = request.json.get('email')

    if not nome or not usuario or not senha or not email:
        return jsonify({"error": "Nome, usuário, email e senha são obrigatórios"}), 400

    if mongo.db.cadastro.find_one({"usuario": usuario}):
        return jsonify({"error": "Usuário já existe"}), 409

    hashed_password = generate_password_hash(senha)
    user_data = {"nome": nome, "usuario": usuario, "senha": hashed_password, "email": email}
    mongo.db.cadastro.insert_one(user_data)
    return jsonify({"msg": "Usuário criado com sucesso!"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Rota para autenticar um usuário usando email ou nome de usuário."""
    data = request.json
    usuario = data.get("usuario")
    senha = data.get("senha")
    
    if not usuario or not senha:
        return jsonify({"error": "Usuario e senha são obrigatórios"}), 400

    user = mongo.db.cadastro.find_one({"$or": [{"usuario": usuario}, {"email": usuario}]} )
    
    if user:
        print(f"Usuário encontrado: {user}")
        if check_password_hash(user['senha'], senha):
            print("Senha correta")
            return jsonify({"msg": "Login realizado com sucesso!"}), 200
        else:
            print("Senha incorreta")
            return jsonify({"error": "Usuario ou senha inválidos"}), 401
    else:
        print("Usuário não encontrado")
        return jsonify({"error": "Usuario ou senha inválidos"}), 401
    

@app.route('/secret')
@requires_auth
def secret_page():
    """Rota protegida que requer autenticação."""
    return {"msg": "Você está autenticado e pode acessar esta página protegida"}

if __name__ == '__main__':
    app.run(debug=True)
