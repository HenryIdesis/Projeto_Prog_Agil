from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from auth import requires_auth, hash_password, init_mongo
from werkzeug.security import generate_password_hash, check_password_hash
import os
from bson.objectid import ObjectId

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


@app.route('/comidas', methods=['GET'])
def get_all_comidas():
    filtro = {}
    projecao = {}
    dados_comidas = mongo.db.comidas.find(filtro, projecao)


    # Converte os documentos do cursor para uma lista e formata o campo '_id' para string
    lista_comidas = []
    for comida in dados_comidas:
        comida['_id'] = str(comida['_id'])
        lista_comidas.append(comida)


    resp = {
        "comidas": lista_comidas
    }


    return resp, 200




@app.route('/comidas/<string:_id>', methods=['GET'])
def get_comida(_id):
   
    user = mongo.db.comidas.find_one({"_id": ObjectId(_id)})


   
    if user is None:
        return {"erro": "comida não encontrada"}, 404
       
   
    user['_id'] = str(user['_id'])
       
    return user, 200




# Este é um exemplo simples sem grandes tratamentos de dados
@app.route('/comidas', methods=['POST'])
def post_comida():
   
    data = request.json
   


    if "nome" not in data:
        return {"erro": "nome é obrigatório"}, 400
    if "preço" not in data:
        return {"erro": "preço é obrigatório"}, 400
    if "estoque" not in data:
        return {"erro": "estoque é obrigatório"}, 400
   
    result = mongo.db.comidas.insert_one(data)


    return {"id": str(result.inserted_id)}, 201




@app.route('/comidas/<string:_id>', methods=['PUT'])
def put_comida(_id):


    data = request.json


    result = mongo.db.comidas.update_one({"_id": ObjectId(_id)}, {"$set": data})
   
    if result.modified_count == 0:
        return {"erro": "comida não encontrado ou nenhuma alteração realizada"}, 404


    return {"message": "comida atualizado com sucesso"}, 200




@app.route('/comidas/<string:_id>', methods=['DELETE'])
def delete_comida(_id):
   
        # Tenta deletar o documento no MongoDB
    result = mongo.db.comidas.delete_one({"_id": ObjectId(_id)})


        # Verifica se um documento foi deletado
    if result.deleted_count == 0:
        return {"erro": "comidas não encontrado"}, 404


    return {"message": "comidas deletado com sucesso"}, 200

# @app.route('/pedidos', methods=['GET'])
# def get_all_pedidos():
#     filtro = {}
#     projecao = {}
#     dados_pedidos = mongo.db.pedidos.find(filtro, projecao)


#     # Converte os documentos do cursor para uma lista e formata o campo '_id' para string
#     lista_pedidos = []
#     for pedido in dados_pedidos:
#         pedido['_id'] = str(pedido['_id'])
#         lista_pedidos.append(pedido)


#     resp = {
#         "pedidos": lista_pedidos
#     }


#     return resp, 200




# @app.route('/pedidos/<string:_id>', methods=['GET'])
# def get_pedido(_id):
   
#     user = mongo.db.pedidos.find_one({"_id": ObjectId(_id)})


   
#     if user is None:
#         return {"erro": "pedido não encontrada"}, 404
       
   
#     user['_id'] = str(user['_id'])
       
#     return user, 200




# # Este é um exemplo simples sem grandes tratamentos de dados
# @app.route('/pedidos', methods=['POST'])
# def post_pedido(id_cadastro, id_comida):
   
#     data = request.json
#     usuario = mongo.db.cadastros.find_one({"_id": ObjectId(id_cadastro)})
#     if not usuario:
#         return {"erro": "Usuário não encontrado"}, 404
    
#     comida = mongo.db.comidas.find_one({"_id": ObjectId(id_comida)})
#     if not comida:
#         return {"erro": "Usuário não encontrado"}, 404


#     if "usuario" not in data:
#         return {"erro": "O nome de usuario é obrigatório"}, 400
#     if "comida" not in data:
#         return {"erro": "A comida é obrigatória"}, 400
   
#     result = mongo.db.pedidos.insert_one(data)


#     return {"id": str(result.inserted_id)}, 201




# @app.route('/pedidos/<string:_id>', methods=['PUT'])
# def put_pedido(_id):


#     data = request.json


#     result = mongo.db.pedidos.update_one({"_id": ObjectId(_id)}, {"$set": data})
   
#     if result.modified_count == 0:
#         return {"erro": "pedido não encontrado ou nenhuma alteração realizada"}, 404


#     return {"message": "pedido atualizado com sucesso"}, 200




# @app.route('/pedidos/<string:_id>', methods=['DELETE'])
# def delete_pedido(_id):
   
#         # Tenta deletar o documento no MongoDB
#     result = mongo.db.pedidos.delete_one({"_id": ObjectId(_id)})


#         # Verifica se um documento foi deletado
#     if result.deleted_count == 0:
#         return {"erro": "pedidos não encontrado"}, 404


#     return {"message": "pedidos deletado com sucesso"}, 200




if __name__ == '__main__':
    app.run(debug=True)
