from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, status, Query
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
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
import hashlib
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

from app.database import engine, get_db
from app import models
from app.utils import gerar_token_seguro, gerar_qr_code_base64, enviar_email_certificado

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tech Sisters Certificados API")

env = Environment(loader=FileSystemLoader("templates"))

BASE_URL_VALIDACAO = os.getenv("BASE_URL_VALIDACAO", "http://localhost:8000")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "techsisters2026")

class CertificadoRequest(BaseModel):
    nome_participante: str
    email_participante: str
    evento: str
    carga_horaria: int = Field(gt=0, description="A carga horária deve ser maior que zero")
    # NOVO CAMPO AQUI
    organizadores: str = "Tech Sisters" 

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

@app.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(verificar_credenciais)])
def pagina_dashboard(q: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Certificado)
    
    if q:
        query = query.filter(
            (models.Certificado.nome_participante.ilike(f"%{q}%")) | 
            (models.Certificado.evento.ilike(f"%{q}%"))
        )
        
    certificados = query.order_by(models.Certificado.id.desc()).all()
    template = env.get_template("dashboard.html")
    html_content = template.render(certificados=certificados, busca=q)
    return HTMLResponse(content=html_content)

@app.post("/admin/revogar/{id}", dependencies=[Depends(verificar_credenciais)])
def revogar_certificado(id: int, db: Session = Depends(get_db)):
    cert = db.query(models.Certificado).filter(models.Certificado.id == id).first()
    if cert:
        cert.status = "revogado"
        db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/admin/editar/{id}", dependencies=[Depends(verificar_credenciais)])
def editar_certificado(id: int, novo_nome: str = Form(...), db: Session = Depends(get_db)):
    cert = db.query(models.Certificado).filter(models.Certificado.id == id).first()
    if cert:
        cert.nome_participante = novo_nome
        db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/gerar-certificado-teste", dependencies=[Depends(verificar_credenciais)])
def gerar_certificado_teste(dados: CertificadoRequest, db: Session = Depends(get_db)):
    try:
        token_bruto, token_hash = gerar_token_seguro(dados.evento, dados.email_participante)
        url_validacao = f"{BASE_URL_VALIDACAO}/validar/{token_bruto}"
        qr_base64 = gerar_qr_code_base64(url_validacao)

        carga_texto = f"{dados.carga_horaria} hora" if dados.carga_horaria == 1 else f"{dados.carga_horaria} horas"

        template = env.get_template("certificado.html")
        html_renderizado = template.render(
            nome_participante=dados.nome_participante,
            evento=dados.evento,
            carga_horaria=carga_texto,
            organizadores=dados.organizadores, # <--- ADICIONADO AQUI
            token=token_bruto,
            qr_code_base64=qr_base64,
            url_validacao=url_validacao
        )

        pdf_bytes = HTML(string=html_renderizado).write_pdf()

        novo_certificado = models.Certificado(
            token=token_hash,
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
        logging.error(f"Erro: {e}")
        raise HTTPException(status_code=500, detail="Erro interno.")

@app.post("/gerar-certificados-em-massa", dependencies=[Depends(verificar_credenciais)])
def gerar_certificados_em_massa(
    arquivo_csv: UploadFile = File(...), 
    evento: str = Form(...),
    carga_horaria: int = Form(..., gt=0),
    organizadores: str = Form("Tech Sisters"), # <--- ADICIONADO AQUI
    db: Session = Depends(get_db)
):
    try:
        df = pd.read_csv(arquivo_csv.file)
        
        if 'nome_participante' not in df.columns or 'email_participante' not in df.columns:
            raise HTTPException(status_code=400, detail="O CSV deve conter 'nome_participante' e 'email_participante'.")

        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for index, row in df.iterrows():
                nome = str(row['nome_participante'])
                email = str(row['email_participante'])
                
                if pd.isna(nome) or pd.isna(email):
                    continue

                token_bruto, token_hash = gerar_token_seguro(evento, email)
                url_validacao = f"{BASE_URL_VALIDACAO}/validar/{token_bruto}"
                qr_base64 = gerar_qr_code_base64(url_validacao)

                carga_texto = f"{carga_horaria} hora" if carga_horaria == 1 else f"{carga_horaria} horas"

                template = env.get_template("certificado.html")
                html_renderizado = template.render(
                    nome_participante=nome,
                    evento=evento,
                    carga_horaria=carga_texto,
                    organizadores=organizadores, # <--- ADICIONADO AQUI
                    token=token_bruto,
                    qr_code_base64=qr_base64,
                    url_validacao=url_validacao
                )

                pdf_bytes = HTML(string=html_renderizado).write_pdf()

                try:
                    enviar_email_certificado(destinatario=email, nome=nome, evento=evento, pdf_bytes=pdf_bytes)
                except Exception as email_error:
                    logging.error(f"Erro email {email}: {email_error}")

                novo_certificado = models.Certificado(
                    token=token_hash,
                    nome_participante=nome,
                    email_participante=email,
                    evento=evento,
                    carga_horaria=carga_horaria
                )
                db.add(novo_certificado)

                nome_limpo = "".join(c for c in nome if c.isalnum() or c in (' ', '_')).rstrip()
                zip_file.writestr(f"certificado_{nome_limpo.replace(' ', '_')}.pdf", pdf_bytes)
            
            db.commit()

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=certificados_evento.zip"}
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validar/{token_bruto}", response_class=HTMLResponse)
def validar_certificado(token_bruto: str, db: Session = Depends(get_db)):
    token_limpo = token_bruto.strip() 
    token_hash = hashlib.sha256(token_limpo.encode()).hexdigest()
    
    certificado = db.query(models.Certificado).filter(models.Certificado.token == token_hash).first()
    template = env.get_template("validacao.html")
    
    if certificado and certificado.status == "ativo":
        html_content = template.render(valido=True, certificado=certificado)
    else:
        html_content = template.render(valido=False)
        
    return HTMLResponse(content=html_content)