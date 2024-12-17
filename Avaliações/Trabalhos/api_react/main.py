from flask import Flask, jsonify, request, session
import jwt
import datetime
import operations
from flask_cors import CORS
from database import init_db

init_db()
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'sua_chave_secreta'

def get_decoded_token():
    token = request.headers.get('Authorization')
    if not token:
        return None, jsonify({"error": "Unauthorized, please provide a token."}), 401

    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        else:
            return None, jsonify({"error": "Invalid token format, please provide a Bearer token."}), 401

        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return decoded_token, None, None
    except jwt.ExpiredSignatureError:
        return None, jsonify({"error": "Token expired, please log in again."}), 401
    except jwt.InvalidTokenError:
        return None, jsonify({"error": "Invalid token, please log in again."}), 401

@app.route('/')
def home():
    session.clear()
    return jsonify({"message": "API Home - Session Cleared"})

@app.route('/api/user/<username>', methods=['GET'])
def user(username):
    return jsonify({"message": f"Hello, {username}!"})

@app.route('/api/about', methods=['GET'])
def about():
    text = 'This is the about page.'
    return jsonify({"message": text})

@app.route('/api/chamada', methods=['GET', 'POST', 'DELETE'])
def chamada():
    decoded_token, error_response, status_code = get_decoded_token()
    if error_response:
        return error_response, status_code

    user_id = decoded_token['user_id']
    is_teacher = decoded_token['isTeacher']

    if not is_teacher:
        teachers = operations.retrieve_professors_for_students(user_id)
        return jsonify({"teachers": teachers})

    if request.method == 'POST':
        data = request.get_json()
        if data['type'] == 'Adicionar':
            novo_nome = data['nome']
            nova_matricula = data['matricula']

            existing_user = operations.get_user_by_nome_matricula(nova_matricula, nome=novo_nome)
            
            if existing_user:
                if existing_user.isTeacher:
                    return jsonify({"error": "Matrícula já existente para um professor"}), 400

                if operations.add_professor_student_relationship_if_exists(user_id, nova_matricula, novo_nome):
                    return jsonify({"message": "Relação com aluno existente adicionada com sucesso"})
                else:
                    return jsonify({"error": "Erro ao adicionar relação com aluno existente"}), 500

            aluno = operations.create_user(nome=novo_nome, senha='default_password', email=f'{novo_nome}@example.com', matricula=nova_matricula, isTeacher=False)
            if aluno:
                if operations.add_professor_student_relationship_if_exists(user_id, aluno.matricula, aluno.nome):
                    return jsonify({"message": "Novo aluno criado e relação adicionada com sucesso"})
                else:
                    return jsonify({"error": "Erro ao adicionar relação com novo aluno"}), 500
            else:
                return jsonify({"error": "Erro ao criar novo aluno"}), 500

    alunos = operations.retrieve_students_for_professor(user_id)
    return jsonify({"alunos": alunos})

@app.route('/api/chamada/<nome>', methods=['DELETE'])
def remove_user(nome):
    decoded_token, error_response, status_code = get_decoded_token()
    if error_response:
        return error_response, status_code

    professor_id = decoded_token['user_id']

    success = operations.remove_professor_aluno_relationship(professor_id, nome)
    if success:
        return jsonify({"message": f"Relação com {nome} removida com sucesso"})
    else:
        return jsonify({"error": f"Falha ao remover relação com {nome}"}), 500

@app.route('/api/presenca/<nome>/<matricula>', methods=['POST'])
def record_presence(nome, matricula):
    decoded_token, error_response, status_code = get_decoded_token()
    if error_response:
        return error_response, status_code

    professor_id = decoded_token['user_id']
    aluno = operations.get_user_by_nome_matricula(matricula, nome)
    if aluno != None:
        professor_aluno_id = operations.get_professor_aluno_id(professor_id, aluno.id)
        print(professor_aluno_id)
        if professor_aluno_id != None:
            success = operations.record_presence(professor_aluno_id)
            if success:
                return jsonify({"message": f"Presença de {nome} registrada com sucesso"})
            else:
                return jsonify({"error": f"Falha ao registrar presença de {nome}"}), 500
    return jsonify({"error": f"Aluno {nome} não encontrado"}), 404

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    matricula = data['matricula']
    password = data['password']

    user = operations.login(matricula=matricula, senha=password)
    if user:
        # Cria o token JWT com payload contendo informações do usuário
        token = jwt.encode({
            'user_id': user.id,
            'username': user.nome,
            'matricula': user.matricula,
            'isTeacher': user.isTeacher,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256").decode('UTF-8')

        return jsonify({
            "message": "Login bem-sucedido",
            "token": token,
            "user": {
                "nome": user.nome,
                "matricula": user.matricula,
                "isTeacher": user.isTeacher
            }
        })
    else:
        return jsonify({"error": "Matrícula ou senha inválidos"}), 401

@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.get_json()
    nome = data['name']
    email = data['email']
    matricula = data['studentNumber']
    password = data['password']
    is_teacher = data['isTeacher']

    user = operations.create_user(nome=nome, senha=password, email=email, matricula=matricula, isTeacher=is_teacher)
    
    if user:
        # Cria o token JWT com payload contendo informações do usuário
        token = jwt.encode({
            'user_id': user.id,
            'username': user.nome,
            'matricula': user.matricula,
            'isTeacher': user.isTeacher,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256").decode('UTF-8')

        return jsonify({
            "message": "Usuário criado com sucesso",
            "token": token,
            "user": {
                "nome": user.nome,
                "matricula": user.matricula,
                "isTeacher": user.isTeacher
            }
        })
    else:
        return jsonify({"error": "Não foi possível criar o usuário."}), 500

if __name__ == '__main__':
    app.run(debug=True)