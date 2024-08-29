from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    senha = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    matricula = Column(String(20), unique=True, nullable=False)
    isTeacher = Column(Boolean, nullable=False)

    __table_args__ = (
        UniqueConstraint('nome', 'matricula', name='_nome_matricula_uc'),
    )
    def __repr__(self):
        return f'<User {self.nome}>'

class ProfessorAluno(Base):
    __tablename__ = 'professor_aluno'

    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    aluno_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    professor = relationship('User', foreign_keys=[professor_id], backref='alunos')
    aluno = relationship('User', foreign_keys=[aluno_id], backref='professores')

    __table_args__ = (UniqueConstraint('professor_id', 'aluno_id', name='_professor_aluno_uc'),)


    def __repr__(self):
        return f'<ProfessorAluno {self.professor_id}-{self.aluno_id}>'

class Presenca(Base):
    __tablename__ = 'presenca'

    id = Column(Integer, primary_key=True)
    dia = Column(Date, default=datetime.utcnow, nullable=False)
    professor_aluno_id = Column(Integer, ForeignKey('professor_aluno.id'), nullable=False)

    professor_aluno = relationship('ProfessorAluno', backref='presencas')

    def __repr__(self):
        return f'<Presenca {self.dia} - {self.professor_aluno_id}>'
