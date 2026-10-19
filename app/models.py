from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Certificado(Base):
    __tablename__ = "certificados"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    nome_participante = Column(String, index=True, nullable=False)
    email_participante = Column(String, nullable=False)
    evento = Column(String, nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    data_emissao = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ativo", nullable=False) 