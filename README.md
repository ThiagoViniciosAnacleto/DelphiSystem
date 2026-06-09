# 🛠️ Delphi System - Modernização de Software

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Pytest](https://img.shields.io/badge/Pytest-Coverage_48%25-green?style=for-the-badge&logo=pytest)
![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions)
![Render](https://img.shields.io/badge/Deploy-Render-black?style=for-the-badge&logo=render)

O **Delphi System** é uma plataforma desenvolvida para o registro de chamados de suporte técnico e apresentação de dashboards operacionais em tempo real. 

Este repositório é fruto de um trabalho prático de **Engenharia Reversa, Reengenharia e Automação DevOps**, realizado para a disciplina de Manutenção de Software (Prof. Jéssica Moraes). O sistema passou por uma transição rigorosa de um "estado legado monolítico" para uma arquitetura moderna, escalável e segura na nuvem.

---

## 🎯 O Desafio da Dívida Técnica
O sistema original apresentava inoperabilidade em produção, ausência de documentação formal e alto nível de acoplamento (dívida técnica). O arquivo principal possuía centenas de linhas concentrando regras de negócio, rotas e acesso ao banco de dados, o que dificultava testes e manutenções seguras.

## 🚀 A Solução e Arquitetura
A base de código foi inteiramente refatorada utilizando os conceitos de Clean Code e Design Patterns. As principais melhorias incluem:

* **Desacoplamento Monolítico:** Separação de responsabilidades em módulos distintos (`auth.py`, `usuarios.py`, `empresas.py`, `cruds.py`).
* **Segurança e JWT:** Implementação de autenticação robusta utilizando `passlib` e `jose`, com proteção rigorosa de segredos de ambiente (`.env` isolado no `.gitignore`).
* **Bypass de Firewall em Nuvem:** Substituição do SMTP tradicional pela API HTTPS do **Brevo (porta 443)** utilizando bibliotecas nativas do Python (`urllib`), contornando bloqueios de porta 587 no provedor em nuvem.
* **Conexão Otimizada de BD:** Utilização de *Internal Database URL* no Render para garantir conexões SSL seguras e sem quedas entre a API e o PostgreSQL.

---

## ⚙️ Tecnologias Utilizadas

* **Backend:** Python, FastAPI, SQLAlchemy (ORM), Alembic (Migrações).
* **Banco de Dados:** PostgreSQL (Hospedado no Render).
* **Segurança:** JWT (JSON Web Tokens), Bcrypt.
* **Testes (V&V):** Pytest, pytest-cov (48% de cobertura atingida com sucesso).
* **CI/CD:** GitHub Actions (Pipeline automatizada para bloquear regressões estruturais).
* **Infraestrutura de E-mail:** Brevo API (via requisições HTTPS nativas).

---

## 🧪 Integração Contínua e Deploy (CI/CD)

O projeto segue um rigoroso padrão de **GitFlow**, com duas branches principais:
1. `main`: Reflete o ambiente de Produção (Live).
2. `dev`: Ambiente de integração e homologação.

Uma esteira automatizada no **GitHub Actions** foi configurada. Sempre que um *Pull Request* é aberto para a branch `main` ou `dev`, o pipeline é ativado para instalar as dependências e executar a suíte de testes do Pytest. O código só é mesclado se não quebrar nenhuma funcionalidade existente (Prevenção de Regressão).

---

## 💻 Como rodar o projeto localmente

### 1. Clone o repositório
```bash
git clone [https://github.com/SeuUsuario/DelphiSystem.git](https://github.com/SeuUsuario/DelphiSystem.git)
cd DelphiSystem

```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate

```

### 3. Instale as dependências

```bash
pip install -r requirements.txt

```

### 4. Configuração das Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz do projeto e preencha com as suas credenciais:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/delphi_db
SECRET_KEY=sua_chave_secreta_aqui
FRONTEND_URL=http://localhost:3000
EMAIL_ORIGEM=seu_email@gmail.com
BREVO_API_KEY=xkeysib-sua-chave-api-aqui

```

### 5. Execute as Migrações do Banco de Dados

```bash
alembic upgrade head

```

### 6. Inicie o Servidor

```bash
uvicorn backend.main:app --reload

```

A API estará disponível em: `http://127.0.0.1:8000/docs`

---

## 🛡️ Executando os Testes

Para verificar a integridade do sistema e gerar o relatório de cobertura de código, execute:

```bash
pytest --cov=backend backend/tests/

```

---

## 👥 Autores

* Thiago Anacleto
* Mylena Alves
* Lucas Vaz