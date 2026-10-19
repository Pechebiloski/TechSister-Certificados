from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Tech Sisters Certificados API")

@app.get("/", response_class=HTMLResponse)
def read_root():
        return """
            <html>
                    <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                                <h1>🚀 API de Certificados da Tech Sisters está rodando!</h1>
                                            <p>Em breve, a automação estará completa por aqui.</p>
                                                    </body>
                                                        </html>
                                                            """