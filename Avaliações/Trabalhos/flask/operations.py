from database import db_session
from models import User, ProfessorAluno, Presenca
from datetime import datetime

def create_user(nome: str, senha: str, email: str, matricula: str, isTeacher: bool):
    """Cria um novo usuário no banco de dados."""
    try:
        user = User(nome=nome, senha=senha, email=email, matricula=matricula, isTeacher=isTeacher)
        db_session.add(user)
        db_session.commit()
        return user
    except Exception as e:
        db_session.rollback()
        print(f"Erro ao criar usuário: {e}")  # Log do erro para depuração
        return None

def login(email: str, senha: str):
    """Realiza o login de um usuário verificando o email e a senha."""
    try:
        user = db_session.query(User).filter_by(email=email, senha=senha).first()
        return user
    except Exception as e:
        print(f"Erro ao realizar login: {e}")  # Log do erro para depuração
        return None

def add_professor_aluno_relationship(professor_id: int, aluno_id: int):
    """Adiciona uma relação entre um professor e um aluno."""
    try:
        relationship = ProfessorAluno(professor_id=professor_id, aluno_id=aluno_id)
        db_session.add(relationship)
        db_session.commit()
        return relationship
    except Exception as e:
        db_session.rollback()
        print(f"Erro ao adicionar relação professor-aluno: {e}")  # Log do erro para depuração
        return None

def record_presence(professor_aluno_id: int, dia: datetime = None):
    """Registra a presença de um aluno em um dia específico."""
    try:
        dia = dia or datetime.utcnow().date()
        presence = Presenca(professor_aluno_id=professor_aluno_id, dia=dia)
        db_session.add(presence)
        db_session.commit()
        return presence
    except Exception as e:
        db_session.rollback()
        print(f"Erro ao registrar presença: {e}")  # Log do erro para depuração
        return None
    
def remove_professor_aluno_relationship(professor_id: int, nome_aluno: str):
    """Remove a relação entre um professor e um aluno, incluindo todas as presenças associadas."""
    try:
        aluno_id = db_session.query(User).filter_by(nome=nome_aluno).first().id
        
        # Inicia uma transação
        with db_session.begin_nested():
            relationship = db_session.query(ProfessorAluno).filter_by(professor_id=professor_id, aluno_id=aluno_id).first()

            if relationship:
                # Primeiro, removemos as presenças associadas a esta relação
                db_session.query(Presenca).filter_by(professor_aluno_id=relationship.id).delete()

                # Depois, removemos a relação entre o professor e o aluno
                db_session.delete(relationship)
            
            db_session.commit()
            return True
        return False
    
    except Exception as e:
        db_session.rollback()
        print(f"Erro ao remover relação professor-aluno: {e}")  # Log do erro para depuração
        return False

def retrieve_students_for_professor(professor_id: int):
    """Recupera todos os alunos que têm uma relação com um professor específico e exibe o número de presenças."""
    try:
        # Recupera todas as relações entre o professor e seus alunos
        relationships = db_session.query(ProfessorAluno).filter_by(professor_id=professor_id).all()
        
        # IDs dos alunos associados ao professor
        aluno_ids = [relationship.aluno_id for relationship in relationships]
        
        # Recupera todos os alunos que não são professores e têm uma relação com o professor
        students = db_session.query(User).filter(User.id.in_(aluno_ids), User.isTeacher == False).all()

        # Cria um dicionário para mapear aluno_id para o número de presenças
        student_presencas = {}
        for relationship in relationships:
            # Conta o número de presenças do aluno
            presencas_count = db_session.query(Presenca).filter_by(professor_aluno_id=relationship.id).count()
            student_presencas[relationship.aluno_id] = presencas_count
        
        # Formata os dados dos alunos com o número de presenças
        formatted_students = {}
        for student in students:
            # Recupera o número de presenças para o aluno
            presencas_count = student_presencas.get(student.id, 0)
            formatted_students[student.nome] = {
                'matricula': student.matricula,
                'presencas': presencas_count
            }

        return formatted_students
    except Exception as e:
        print(f"Erro ao recuperar alunos para o professor: {e}")  # Log do erro para depuração
        return {}
    
def retrieve_professors_for_students(student_id: int):
    """Recupera todos os professores associados a um aluno específico e exibe o número de presenças com cada professor."""
    try:
        # Recupera todas as relações entre o aluno e seus professores
        relationships = db_session.query(ProfessorAluno).filter_by(aluno_id=student_id).all()
        
        # IDs dos professores associados ao aluno
        professor_ids = [relationship.professor_id for relationship in relationships]
        
        # Recupera todos os professores que têm uma relação com o aluno
        professors = db_session.query(User).filter(User.id.in_(professor_ids), User.isTeacher == True).all()

        # Cria um dicionário para mapear professor_id para o número de presenças
        professor_presencas = {}
        for relationship in relationships:
            # Conta o número de presenças do aluno com o professor
            presencas_count = db_session.query(Presenca).filter_by(professor_aluno_id=relationship.id).count()
            professor_presencas[relationship.professor_id] = presencas_count
        
        # Formata os dados dos professores com o número de presenças
        formatted_professors = {}
        for professor in professors:
            # Recupera o número de presenças para o aluno com o professor
            presencas_count = professor_presencas.get(professor.id, 0)
            formatted_professors[professor.nome] = presencas_count

        return formatted_professors
    except Exception as e:
        print(f"Erro ao recuperar professores para o aluno: {e}")  # Log do erro para depuração
        return {}
    
def get_user_by_nome_matricula(matricula: str,  nome: str):
    """Recupera um usuário pelo número de matrícula."""
    try:
        user = db_session.query(User).filter_by(matricula=matricula, nome=nome).first()
        return user
    except Exception as e:
        print(f"Erro ao recuperar usuário por matrícula: {e}")  # Log do erro para depuração
        return None

def add_professor_student_relationship_if_exists(professor_id: int, matricula: str, nome: str):
    """Adiciona uma relação entre um professor e um aluno se o aluno existir."""
    try:
        user = get_user_by_nome_matricula(matricula, nome)
        checkIfAlreadyExists = db_session.query(ProfessorAluno).filter_by(professor_id=professor_id, aluno_id=user.id).first()
        if checkIfAlreadyExists:
            return True
        if user and not user.isTeacher:
            relationship = add_professor_aluno_relationship(professor_id, user.id)
            return relationship is not None
        return False
    except Exception as e:
        print(f"Erro ao adicionar relação professor-aluno: {e}")  # Log do erro para depuração
        return False
    
def get_user_by_nome(nome: str):
    """Recupera um usuário pelo nome."""
    try:
        return db_session.query(User).filter_by(nome=nome).first()
    except Exception as e:
        print(f"Erro ao recuperar usuário por nome: {e}")
        return None

def get_professor_aluno_id(professor_id: int, aluno_id: int):
    """Obtém o ID da relação entre professor e aluno."""
    try:
        relationship = db_session.query(ProfessorAluno).filter_by(professor_id=professor_id, aluno_id=aluno_id).first()
        return relationship.id if relationship else None
    except Exception as e:
        print(f"Erro ao recuperar relação professor-aluno: {e}")
        return None