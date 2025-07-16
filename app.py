from flask import Flask, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from models.user import User
from database import db
from login import login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'



db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return jsonify({"message": "Autenticação realizada com sucesso"})

    return jsonify({"message": "Credenciais invalidas"}), 400


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso"})


@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso"}), 201
    return jsonify({"message": "Dados invalidos" }), 400

@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User().query.get(id_user)
    if id_user == current_user.id:
        return jsonify({"message": f"Deleção não permitida"}), 403
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} deletado com sucesso"}), 200
    return jsonify({"message": "Usuário não encontrado" }), 400

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    user = User().query.get(id_user)
    data = request.json
    password = data.get('password')
    if user and password:
        user.password = password
        db.session.commit()
        return jsonify({"message": f"Usuário {user.username} atualizado com sucesso"}), 200
    return jsonify({"message": "Usuário não encontrado" }), 404

@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = User().query.get(id_user)
    if user:
        return jsonify({"username": user.username}), 200
    return jsonify({"message": "Usuário não encontrado" }), 404

@app.route("/user", methods=["GET"])
@login_required
def all_users():
    users = User().query.all()
    user_list = [user.id for user in users]
    if users:
        return jsonify(user_list), 200
    return jsonify({"message": "Dados invalidos" }), 400

if __name__ ==  '__main__':
    app.run(debug=True)