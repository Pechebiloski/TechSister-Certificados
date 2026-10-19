<div align="center">

# ♡ Tech Sisters — Automação de Certificados

**«Uma solução em Python para automatizar a emissão, o envio e a validação de certificados dos eventos da comunidade Tech Sisters.»**

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-pink?style=for-the-badge)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

*Tecnologia para simplificar processos e fortalecer comunidades.*
</div>

---

### 🎀 "01" · Sobre o projeto

O **Tech Sisters — Automação de Certificados** é um projeto voltado à modernização do fluxo de emissão de certificados da comunidade, reduzindo tarefas manuais e tornando o processo mais eficiente, consistente e seguro.

Atualmente, a emissão depende de ajustes manuais em modelos de documentos, o que dificulta a manutenção da identidade visual e aumenta o tempo necessário para atender às participantes.

A proposta é desenvolver uma API capaz de centralizar esse processo, desde a geração dos documentos até a verificação de autenticidade.

### 🧩 "02" · O problema

O fluxo atual apresenta alguns desafios:
*   **Processos manuais:** Tempo excessivo dedicado à edição e emissão dos certificados.
*   **Manutenção visual:** Dificuldade para atualizar os documentos quando a identidade visual da comunidade muda.
*   **Escalabilidade:** Limitações para gerar certificados em grandes quantidades.
*   **Autenticidade:** Ausência de um mecanismo integrado para verificar a validade dos documentos.

### 💡 "03" · A solução

Uma API desenvolvida em Python para automatizar as principais etapas do processo.

| Funcionalidade | Descrição |
| :--- | :--- |
| **Templates flexíveis** | Certificados gerados a partir de HTML e CSS, facilitando a manutenção visual. |
| **Geração em lote** | Leitura de listas de presença em CSV e geração automatizada de PDFs. |
| **Validação individual** | Identificador único para cada certificado, com suporte a QR Codes. |
| **Verificação pública** | Endpoint para consultar a autenticidade de um certificado. |
| **Envio automatizado** | Preparação para o envio de certificados por e-mail com documentos anexados. |

> ♡ *A arquitetura busca manter a lógica de negócio independente da apresentação visual, facilitando futuras atualizações e melhorias.*

### 🛠️ "04" · Tecnologias

As ferramentas escolhidas para a implementação:

| Tecnologia | Aplicação |
| :--- | :--- |
| 🐍 **[Python](https://www.python.org/)** | Linguagem principal |
| ⚡ **[FastAPI](https://fastapi.tiangolo.com/)** | Construção da API |
| 🎨 **[Jinja2](https://jinja.palletsprojects.com/)** | Renderização de templates HTML |
| 📄 **[WeasyPrint](https://weasyprint.org/)** | Conversão de HTML/CSS para PDF |
| 🗄️ **[SQLAlchemy](https://www.sqlalchemy.org/)** | Mapeamento objeto-relacional (ORM) |
| 💾 **[SQLite](https://www.sqlite.org/)** | Persistência dos dados |
| 🔳 **[qrcode](https://pypi.org/project/qrcode/)** | Geração de QR Codes |
| 🖼️ **[Pillow](https://pypi.org/project/Pillow/)** | Processamento de imagens |
| 🔐 **[python-dotenv](https://pypi.org/project/python-dotenv/)** | Gerenciamento de variáveis de ambiente |

### 📁 "05" · Estrutura do projeto

```text
tech-sisters-certificados/
│
├── app/
│   ├── main.py          # Rotas da API
│   ├── database.py      # Configuração do banco de dados
│   ├── models.py        # Modelos de dados
│   └── utils.py         # Hashes e geração de QR Codes
│
├── templates/
│   └── certificado.html # Template do certificado
│
├── static/
│   └── css/             # Estilos dos documentos
│
├── .env.example         # Exemplo de configuração
├── requirements.txt     # Dependências Python
└── README.md
