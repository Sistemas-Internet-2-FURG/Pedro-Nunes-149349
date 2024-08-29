from flask import Flask, flash, json, render_template, redirect, session, request, url_for
from database import init_db
import operations

init_db()
app = Flask(__name__)

app.secret_key = 'adim'

# abrir o json e lê os dados
# with open('alunos.json', 'r') as f:
#     alunos = json.load(f)

@app.route('/')
def home():
    session.clear()
    return render_template('home.html')

@app.route('/user/<username>')
def user(username):
    return f'Hello, {username}!'

@app.route('/about')
def about():
    text = 'This is the about page.'
    return render_template('about.html', text=text)

# ROUTE TO ADD
@app.route('/chamada', methods=['GET', 'POST', 'DELETE'])
def chamada():
    if not session.get('username'):
        return redirect(url_for('login'))
    if not session.get('isTeacher'):
        teachers = operations.retrieve_professors_for_students(session.get('user_id'))
        return render_template('chamadaAluno.html', teachers=teachers)
    professor_id = session.get('user_id')

    if request.method == 'POST' and request.form.get('type') == 'Adicionar':
        novo_nome = request.form['nome']
        nova_matricula = request.form['matricula']

        # Verificar se o usuário já existe
        existing_user = operations.get_user_by_nome_matricula(nova_matricula, nome=novo_nome)
        
        if existing_user:
            if existing_user.isTeacher:
                alunos = operations.retrieve_students_for_professor(professor_id)
                return render_template('chamada.html', alunos=alunos, error='Matrícula já existente para um professor')
            
            # Adicionar relação se o usuário for aluno
            if operations.add_professor_student_relationship_if_exists(professor_id, nova_matricula, novo_nome):
                alunos = operations.retrieve_students_for_professor(professor_id)
                return render_template('chamada.html', alunos=alunos, success='Relação com aluno existente adicionada com sucesso')
            else:
                alunos = operations.retrieve_students_for_professor(professor_id)
                return render_template('chamada.html', alunos=alunos, error='Erro ao adicionar relação com aluno existente')
        
        # Criar novo aluno e adicionar relação
        aluno = operations.create_user(nome=novo_nome, senha='default_password', email=f'{novo_nome}@example.com', matricula=nova_matricula, isTeacher=False)
        if aluno:
            # Adicionar relação com o novo aluno
            if operations.add_professor_student_relationship_if_exists(professor_id, aluno.matricula, aluno.nome):
                alunos = operations.retrieve_students_for_professor(professor_id)
                return render_template('chamada.html', alunos=alunos, success='Novo aluno criado e relação adicionada com sucesso')
            else:
                alunos = operations.retrieve_students_for_professor(professor_id)
                return render_template('chamada.html', alunos=alunos, error='Erro ao adicionar relação com novo aluno')
        else:
            alunos = operations.retrieve_students_for_professor(professor_id)
            return render_template('chamada.html', alunos=alunos, error='Erro ao criar novo aluno')

    # Para métodos GET e DELETE, ou se o método POST não for 'Adicionar', apenas renderiza a lista de alunos
    alunos = operations.retrieve_students_for_professor(professor_id)
    return render_template('chamada.html', alunos=alunos, session=session)


# ROUTE TO DELETE
@app.route('/chamada/<nome>', methods=['POST'])
def removeUser(nome):
    '''Remove a relação entre um professor e um aluno.'''
    professor_id = session.get('user_id')
    if request.method == 'POST':
        success = operations.remove_professor_aluno_relationship(professor_id, nome)
        # if success:
        #     alunos = operations.retrieve_students_for_professor(professor_id)
        #     return render_template('chamada.html', alunos=alunos)
        # else:
        #     alunos = operations.retrieve_students_for_professor(professor_id)
        #     return render_template('chamada.html', alunos=alunos)
    return redirect(url_for('chamada'))

# ROUTE TO RECORD PRESENCE
@app.route('/presenca/<nome>', methods=['POST'])
def recordPresence(nome):
    '''Registra a presença de um aluno.'''
    professor_id = session.get('user_id')
    aluno = operations.get_user_by_nome(nome)
    if aluno:
        professor_aluno_id = operations.get_professor_aluno_id(professor_id, aluno.id)
        if professor_aluno_id:
            success = operations.record_presence(professor_aluno_id)
            if success:
                flash(f'Presença de {nome} registrada com sucesso!')
            else:
                flash(f'Falha ao registrar presença de {nome}.')
    return redirect(url_for('chamada'))


# ROUTE TO LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']


        # Verificar o login do usuário
        user = operations.login(email=email, senha=password)
        if user:
            session['username'] = user.nome
            session['matricula'] = user.matricula  # Armazenar a matrícula do aluno na sessão
            session['user_id'] = user.id
            session['isTeacher'] = user.isTeacher
            app.secret_key = email
            return redirect('chamada') 
        else:
            return render_template('login.html', error='Email ou senha inválidos')

# ROUTE TO SIGNIN
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        matricula = request.form['studentNumber']
        password = request.form['password']
        is_teacher = 'isTeacher' in request.form  # Verifica se o checkbox está marcado
        # Criar o usuário
        user = operations.create_user(nome=nome, senha=password, email=email, matricula=matricula, isTeacher=is_teacher)
        
        if user:            
            session['username'] = user.nome
            session['matricula'] = user.matricula  # Armazenar a matrícula do aluno na sessão
            session['user_id'] = user.id
            session['isTeacher'] = user.isTeacher
            app.secret_key = email  # Usar o email como chave secreta para a sessão
            return redirect('chamada') 
        else:
            return render_template('signin.html', error='Não foi possível criar o usuário.')



if __name__ == '__main__':
    app.run(debug=True) 