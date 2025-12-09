SGEA – Sistema de Gestão de Eventos Acadêmicos

Plataforma web desenvolvida em Django para gerenciamento completo de eventos, incluindo cadastro, inscrições, geração de certificados, autenticação, restrições por papel de usuário, upload de imagens, integração com templates, e controle administrativo.

1. Visão Geral

O SGEA é um sistema web destinado a instituições que desejam organizar eventos, gerenciar participantes e emitir certificados automaticamente.
A aplicação oferece:

CRUD completo de eventos.

Sistema de inscrições com controle de vagas.

Upload e exibição de banners.

Módulo administrativo (staff).

Autenticação com Django padrão + níveis de permissão.

Geração de certificados em PDF.

Painel do usuário com eventos inscritos.

Templates responsivos com Bootstrap.

API JWT opcional (projeto inclui dependências de DRF e SimpleJWT).

2. Tecnologias Utilizadas

Backend:

Python

Django

Django REST Framework (se aplicável)

SimpleJWT (opcional, presente no projeto)

Frontend:

HTML, CSS, JavaScript

Bootstrap 5

Django Templates

Banco de Dados:

SQLite (desenvolvimento)

PostgreSQL recomendado em produção

Ferramentas auxiliares:

Virtualenv

Pillow (para upload de imagens)

ReportLab (para geração de certificados em PDF)

3. Arquitetura do Projeto

Estrutura típica encontrada no projeto:

sgea_project_final2_1/
│ manage.py
│ db.sqlite3
│ requirements.txt
│
├── core/                 # Configurações gerais do Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── events/               # Aplicação principal
│   ├── models.py         # Modelos: Evento, Inscrição, Certificado etc.
│   ├── views.py          # Regras de listagem, cadastro e geração de certificado
│   ├── urls.py
│   ├── forms.py
│   ├── templates/events/
│   │   ├── event_list.html
│   │   ├── event_detail.html
│   │   └── certificate.html
│   └── static/events/
│       └── css / js / imagens
│
├── accounts/             # Módulo de autenticação
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── templates/accounts/
│
└── media/                # Banners enviados

4. Funcionalidades Implementadas
4.1 Eventos

Cadastro de eventos com:

título

descrição

data

carga horária

banner (upload)

limite de vagas

Listagem pública e detalhamento.

4.2 Inscrições

Usuários autenticados podem se inscrever.

Controle de limite de vagas.

Restrição: não pode se inscrever duas vezes.

Painel "Meus Eventos".

4.3 Certificados

Geração automática de PDF.

Template HTML para renderização.

Campos dinâmicos:

nome do participante

nome do evento

carga horária

data


4.4 Administradores

CRUD completo pelo Django Admin.

Permissões específicas por tipo de usuário.

Upload de banners diretamente no painel.

4.5 Autenticação

Sistema completo:

registro

login

logout



Pode utilizar SimpleJWT para API móvel.

5. Instalação e Configuração
5.1 Clonar o repositório
git clone https://github.com/majuccosta/sgea.git
cd sgea

5.2 Criar ambiente virtual
python -m venv venv


Para ativar:

Windows:

venv\Scripts\activate


5.3 Instalar dependências
pip install -r requirements.txt

5.4 Executar migrações
python manage.py migrate

5.5 Criar superusuário
python manage.py createsuperuser

5.6 Executar o servidor
python manage.py runserver

5.7 Para ver parte da auditoria 
http://127.0.0.1:8000/logs/
















