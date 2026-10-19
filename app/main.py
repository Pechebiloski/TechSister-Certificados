from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from pydantic import BaseModel, Field
import urllib.parse
import pandas as pd
import zipfile
import os
import secrets
import logging
from dotenv import load_dotenv

# Carrega o .env ANTES de qualquer coisa
load_dotenv()

from app.database import engine, get_db
from app import models
from app.utils import gerar_token_seguro, gerar_qr_code_base64, enviar_email_certificado

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tech Sisters Certificados API")

env = Environment(loader=FileSystemLoader("templates"))

# Pega as variáveis do .env com fallback seguro
BASE_URL_VALIDACAO = os.getenv("BASE_URL_VALIDACAO", "http://localhost:8000")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "techsisters2026")

class CertificadoRequest(BaseModel):
    nome_participante: str
    email_participante: str
    evento: str
    carga_horaria: int = Field(gt=0, description="A carga horária deve ser maior que zero")

# --- SEGURANÇA ---
security = HTTPBasic()

def verificar_credenciais(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- ROTAS ---
@app.get("/")
def read_root():
    return {"status": "Online", "message": "API de Certificados Tech Sisters rodando!"}

@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(verificar_credenciais)])
def pagina_admin():
    with open("templates/admin.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

# Adicionado 'dependencies' para proteger a rota!
@app.post("/gerar-certificado-teste", dependencies=[Depends(verificar_credenciais)])
def gerar_certificado_teste(dados: CertificadoRequest, db: Session = Depends(get_db)):
    try:
        token = gerar_token_seguro(dados.evento, dados.email_participante)
        url_validacao = f"{BASE_URL_VALIDACAO}/validar/{token}"
        qr_base64 = gerar_qr_code_base64(url_validacao)

        template = env.get_template("certificado.html")
        html_renderizado = template.render(
            nome_participante=dados.nome_participante,
            evento=dados.evento,
            carga_horaria=dados.carga_horaria,
            token=token,
            qr_code_base64=qr_base64,
            url_validacao=url_validacao # Passando a URL para o template
        )

        pdf_bytes = HTML(string=html_renderizado).write_pdf()

        novo_certificado = models.Certificado(
            token=token,
            nome_participante=dados.nome_participante,
            email_participante=dados.email_participante,
            evento=dados.evento,
            carga_horaria=dados.carga_horaria
        )
        db.add(novo_certificado)
        db.commit()

        nome_seguro = urllib.parse.quote(f"certificado_{dados.nome_participante}.pdf")

        return StreamingResponse(
            BytesIO(pdf_bytes), 
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{nome_seguro}"}
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao gerar certificado individual: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar certificado.")

# Adicionado 'dependencies' para proteger a rota!
@app.post("/gerar-certificados-em-massa", dependencies=[Depends(verificar_credenciais)])
def gerar_certificados_em_massa(
    arquivo_csv: UploadFile = File(...), 
    evento: str = Form(...),
    carga_horaria: int = Form(..., gt=0),
    db: Session = Depends(get_db)
):
    try:
        df = pd.read_csv(arquivo_csv.file)
        
        # Validação básica do CSV
        if 'nome_participante' not in df.columns or 'email_participante' not in df.columns:
            raise HTTPException(status_code=400, detail="O CSV deve conter as colunas 'nome_participante' e 'email_participante'.")

        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for index, row in df.iterrows():
                nome = str(row['nome_participante'])
                email = str(row['email_participante'])
                
                if pd.isna(nome) or pd.isna(email):
                    continue # Pula linhas vazias

                token = gerar_token_seguro(evento, email)
                url_validacao = f"{BASE_URL_VALIDACAO}/validar/{token}"
                qr_base64 = gerar_qr_code_base64(url_validacao)

                template = env.get_template("certificado.html")
                html_renderizado = template.render(
                    nome_participante=nome,
                    evento=evento,
                    carga_horaria=carga_horaria,
                    token=token,
                    qr_code_base64=qr_base64,
                    url_validacao=url_validacao
                )

                pdf_bytes = HTML(string=html_renderizado).write_pdf()

                try:
                    enviar_email_certificado(
                        destinatario=email, 
                        nome=nome, 
                        evento=evento, 
                        pdf_bytes=pdf_bytes
                    )
                except Exception as email_error:
                    logging.error(f"Erro ao enviar email para {email}: {email_error}")

                novo_certificado = models.Certificado(
                    token=token,
                    nome_participante=nome,
                    email_participante=email,
                    evento=evento,
                    carga_horaria=carga_horaria
                )
                db.add(novo_certificado)

                # Sanitização básica do nome do arquivo
                nome_limpo = "".join(c for c in nome if c.isalnum() or c in (' ', '_')).rstrip()
                nome_arquivo_zip = f"certificado_{nome_limpo.replace(' ', '_')}.pdf"
                zip_file.writestr(nome_arquivo_zip, pdf_bytes)
            
            db.commit()

        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=certificados_evento.zip"}
        )
        
    except HTTPException:
        raise # Repassa erros de validação (como o do CSV)
    except Exception as e:
        db.rollback()
        logging.error(f"Erro na geração em massa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar o lote.")

@app.get("/validar/{token}", response_class=HTMLResponse)
def validar_certificado(token: str, db: Session = Depends(get_db)):
    token_limpo = token.strip() 
    certificado = db.query(models.Certificado).filter(models.Certificado.token == token_limpo).first()
    template = env.get_template("validacao.html")
    
    if certificado:
        html_content = template.render(valido=True, certificado=certificado)
    else:
        html_content = template.render(valido=False)
        
    return HTMLResponse(content=html_content)