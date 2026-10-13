# 🚀 API de Rede Social - Projeto Final EBAC

API RESTful completa desenvolvida com **Django** e **Django REST Framework (DRF)** para gerenciamento de usuários, perfis, postagens, comentários, curtidas e sistema de seguidores.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python
- **Framework:** Django & Django REST Framework (DRF)
- **Gerenciador de Dependências:** Poetry
- **Autenticação:** JWT (`rest_framework_simplejwt`)
- **Documentação:** OpenAPI 3.0 / Swagger UI / ReDoc (`drf-spectacular`)
- **Imagens:** Pillow (`ImageField` para foto de perfil)
- **Configurações:** `python-decouple` (Variáveis de ambiente)
- **Banco de Dados:** SQLite (Desenvolvimento/Testes)

---

## 📋 Funcionalidades

### 🔐 Autenticação & Usuários (`/api/accounts/`)
- Registro de novos usuários.
- Login e obtenção de pares de tokens JWT (`access` e `refresh`).
- Atualização do token via endpoint de refresh.
- Edição de dados do próprio perfil (`/api/accounts/me/`) com upload de avatar.
- Sistema de **Seguir / Deixar de seguir** (`/api/accounts/users/<id>/follow/`).

### 📝 Publicações & Interações (`/api/`)
- **Posts:** CRUD completo de postagens com suporte a busca, ordenação e paginação.
- **Feed:** Listagem de posts com otimização contra consultas *N+1*.
- **Meus Posts:** Rota dedicada para listar as postagens do usuário autenticado (`/api/posts/me/`).
- **Comentários:** Criação e gestão de comentários vinculados a postagens.
- **Curtidas:** Sistema de alternância (*toggle*) para curtir e descurtir postagens.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.10+
- Poetry instalado

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
   cd NOME_DO_REPOSITORIO