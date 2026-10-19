# Tech Sisters - Automação de Certificados

Uma solução completa em Python para automatizar a emissão, o envio, a validação e o gerenciamento de certificados dos eventos da comunidade Tech Sisters.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-MVP_Concluído-pink?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

---

## Demonstração do Sistema

Aqui estão algumas capturas de tela do sistema em funcionamento:

| Painel Administrativo | Dashboard de Gerenciamento |
| :---: | :---: |
| <img src="assets/admin.png" width="400" alt="Tela de Admin"> | <img src="assets/dashboard.png" width="400" alt="Dashboard"> |
| *Interface amigável para upload de CSV e configuração do evento.* | *Painel com busca, edição rápida e revogação de certificados.* |

| Certificado Gerado (PDF) | Página Pública de Validação |
| :---: | :---: |
| <img src="assets/certificado.png" width="400" alt="Certificado PDF"> | <img src="assets/validacao.png" width="400" alt="Tela de Validação"> |
| *Certificado gerado dinamicamente com QR Code de autenticidade.* | *Validação pública com mascaramento de dados (LGPD).* |

*(Nota: substitua os caminhos `assets/imagem.png` se você colocar as imagens em outra pasta).*

---

## "01" - Sobre o projeto

O **Tech Sisters - Automação de Certificados** moderniza o fluxo de emissão de certificados da comunidade, reduzindo tarefas manuais e garantindo segurança na validação. 

O sistema resolve gargalos operacionais, como a emissão em lote, a padronização visual flexível (permitindo mudar o layout sem alterar o código) e a proteção dos dados das participantes.

## "02" - Funcionalidades Principais

- **Geração em Lote:** Leitura de planilhas (CSV) do Google Forms e geração automatizada de PDFs.
- **Design Flexível:** Templates em HTML/CSS. O layout inclui um campo dinâmico de "Realização / Parceria", adaptando-se a eventos conjuntos.
- **Envio Automatizado:** Disparo de e-mails personalizados com o certificado em anexo.
- **QR Code de Validação:** Cada certificado possui um código único criptográfico.
- **Painel Administrativo (`/admin`):** Interface protegida por senha para emissão em massa.
- **Dashboard (`/dashboard`):** Visualização de todos os certificados, com busca por nome/evento, edição em linha (correção de nomes) e revogação de certificados.
- **Validação Pública:** Página de verificação acessível via QR Code.

## "03" - Segurança e LGPD

A arquitetura foi pensada para proteger os dados das participantes:

- **Tokens Criptográficos:** O sistema gera um token aleatório de 256 bits (via `secrets`). O banco de dados armazena apenas o hash SHA-256 desse token, nunca o valor real.
- **Privacidade (LGPD):** A página pública de validação exibe apenas o primeiro nome e a inicial do sobrenome da participante (ex: "Maria S."), além de omitir dados sensíveis.
- **Proteção de Rotas:** As rotas de administração e geração utilizam HTTP Basic Auth (usuário e senha configurados via variáveis de ambiente).
- **Revogação:** Certificados podem ser revogados no dashboard. Se o QR Code for escaneado, a página indicará que o documento é inválido.

## "04" - Tecnologias Utilizadas

| Tecnologia | Aplicação |
| :--- | :--- |
| **Python** | Linguagem principal do backend. |
| **FastAPI** | Framework web para construção da API e rotas. |
| **Jinja2** | Renderização dos templates HTML. |
| **WeasyPrint** | Conversão de HTML/CSS em PDFs de alta qualidade. |
| **SQLAlchemy + SQLite** | ORM e banco de dados (pronto para migrar para PostgreSQL em produção). |
| **qrcode + Pillow** | Geração e processamento dos QR Codes. |
| **Pandas** | Leitura e tratamento das planilhas CSV. |
| **smtplib** | Envio de e-mails (com testes realizados via Mailtrap). |

## "05" - Como executar o projeto localmente

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/tech-sisters-certificados.git
cd tech-sisters-certificados
Crie e ative um ambiente virtual:

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
Instale as dependências:

bash
pip install -r requirements.txt
Instale as dependências do sistema (necessárias para o WeasyPrint no Linux/Codespaces):

bash
sudo apt-get update && sudo apt-get install -y libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libgdk-pixbuf2.0-0
Configure o .env (use o .env.example como base):

bash
cp .env.example .env
(Preencha as credenciais de SMTP e defina as senhas de administrador).

Inicie o servidor:

bash
uvicorn app.main:app --reload
Acesse http://127.0.0.1:8000/admin para a interface de emissão.

"06" - Roadmap
☑ Estrutura inicial e modelagem do banco de dados.
☑ Geração de PDF individual e em massa (ZIP).
☑ Integração com WeasyPrint e design customizado.
☑ Página de validação pública via QR Code (com LGPD).
☑ Disparo de e-mail com anexo.
☑ Implementação de segurança (Hash SHA-256, Basic Auth).
☑ Dashboard de gerenciamento com busca, edição e revogação.
□ Deploy em nuvem (Render/Railway) com PostgreSQL.
□ Integração direta com a API do Google Sheets.
Desenvolvido com dedicação para a comunidade Tech Sisters.