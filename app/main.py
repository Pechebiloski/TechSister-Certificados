from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from pydantic import BaseModel
import urllib.parse
import pandas as pd
import zipfile
import os

from app.database import engine, get_db
from app import models
from app.utils import gerar_token_seguro, gerar_qr_code_base64

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tech Sisters Certificados API")

env = Environment(loader=FileSystemLoader("templates"))

class CertificadoRequest(BaseModel):
    nome_participante: str
    email_participante: str
    evento: str
    carga_horaria: int

@app.get("/")
def read_root():
    return {"status": "Online", "message": "API de Certificados Tech Sisters rodando!"}


@app.post("/gerar-certificado-teste")
def gerar_certificado_teste(dados: CertificadoRequest, db: Session = Depends(get_db)):
    try:
        token = gerar_token_seguro(dados.evento, dados.email_participante)
        url_validacao = f"https://techsisters.com.br/validar/{token}"
        qr_base64 = gerar_qr_code_base64(url_validacao)

        template = env.get_template("certificado.html")
        html_renderizado = template.render(
            nome_participante=dados.nome_participante,
            evento=dados.evento,
            carga_horaria=dados.carga_horaria,
            token=token,
            qr_code_base64=qr_base64
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
        return {"erro": str(e)}


@app.post("/gerar-certificados-em-massa")
def gerar_certificados_em_massa(
    arquivo_csv: UploadFile = File(...), 
    evento: str = Form(...),
    carga_horaria: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
     
        df = pd.read_csv(arquivo_csv.file)
        
      
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # 3. Itera sobre cada linha da planilha
            for index, row in df.iterrows():
                nome = row['nome_participante']
                email = row['email_participante']
                
                token = gerar_token_seguro(evento, email)
                url_validacao = f"https://techsisters.com.br/validar/{token}"
                qr_base64 = gerar_qr_code_base64(url_validacao)

                template = env.get_template("certificado.html")
                html_renderizado = template.render(
                    nome_participante=nome,
                    evento=evento,
                    carga_horaria=carga_horaria,
                    token=token,
                    qr_code_base64=qr_base64
                )

                pdf_bytes = HTML(string=html_renderizado).write_pdf()

               
                novo_certificado = models.Certificado(
                    token=token,
                    nome_participante=nome,
                    email_participante=email,
                    evento=evento,
                    carga_horaria=carga_horaria
                )
                db.add(novo_certificado)

           
                nome_arquivo_zip = f"certificado_{nome.replace(' ', '_')}.pdf"
                zip_file.writestr(nome_arquivo_zip, pdf_bytes)
            
        
            db.commit()

        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=certificados_evento.zip"}
        )
        
    except Exception as e:
        db.rollback()
        return {"erro": str(e)}