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