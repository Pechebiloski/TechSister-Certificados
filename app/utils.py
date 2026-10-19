import hashlib
import os
import qrcode
from io import BytesIO
import base64
import secrets
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def gerar_token_seguro(evento: str, email: str):
    """
    Gera um token aleatório de 256 bits e retorna (token_bruto, hash_do_token).
    O token_bruto vai para o QR Code. O hash vai para o banco de dados.
    """
    # Gera 256 bits de aleatoriedade criptográfica (impossível de adivinhar)
    token_bruto = secrets.token_urlsafe(32)
    # O banco de dados só guarda o hash, nunca o token original
    token_hash = hashlib.sha256(token_bruto.encode()).hexdigest()
    
    return token_bruto, token_hash

def gerar_qr_code_base64(texto_url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(texto_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

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
    nome_arquivo = f"certificado_{nome.replace(' ', '_')}.pdf"
    msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=nome_arquivo)
    
    try:
        # Adicionado timeout=10 para não travar o servidor se o e-mail falhar
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')), timeout=10) as server:
            server.starttls() 
            server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
            print(f"✅ E-mail enviado com sucesso para {destinatario}")
    except Exception as e:
        print(f"❌ Falha ao enviar e-mail para {destinatario}: {e}")