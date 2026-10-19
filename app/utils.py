import hashlib
import os
import qrcode
from io import BytesIO
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def gerar_token_seguro(evento: str, email: str) -> str:
    """Gera um hash SHA-256 único usando dados do aluno e um 'salt' secreto."""
    salt = os.getenv("SECRET_SALT", "salt_padrao")
    raw_data = f"{salt}-{evento}-{email}-{datetime.now().isoformat()}"
    return hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

def gerar_qr_code_base64(texto_url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(texto_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


    # ... (mantenha os imports que já estão no topo do arquivo) ...
import smtplib
from email.message import EmailMessage

# ... (mantenha as funções gerar_token_seguro e gerar_qr_code_base64) ...

def enviar_email_certificado(destinatario: str, nome: str, evento: str, pdf_bytes: bytes):
    """Envia o certificado em anexo por e-mail."""
    msg = EmailMessage()
    msg['Subject'] = f'Seu certificado do evento {evento} chegou! 🎉'
    msg['From'] = os.getenv('SMTP_USER')
    msg['To'] = destinatario
    
    corpo = f"""Olá, {nome}!

É com muita alegria que enviamos o seu certificado de participação do evento {evento}.

Em anexo você encontrará o seu certificado em PDF. Ele possui um QR Code de validação autêntica.

Com carinho,
Equipe Tech Sisters 💖
"""
    msg.set_content(corpo)
    
    # Anexa o PDF
    nome_arquivo = f"certificado_{nome.replace(' ', '_')}.pdf"
    msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=nome_arquivo)
    
    # Conecta ao servidor e envia
    try:
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.starttls() # Criptografia
            server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
            print(f"✅ E-mail enviado com sucesso para {destinatario}")
    except Exception as e:
        print(f"❌ Falha ao enviar e-mail para {destinatario}: {e}")