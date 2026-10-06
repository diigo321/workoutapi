# Workout API — FastAPI, Python e Docker

Projeto do bootcamp Vivo — Python AI Backend Developer da DIO, baseado no [projeto original da DIO](https://github.com/digitalinnovationone/workout_api), com as melhorias solicitadas no desafio.

## Funcionalidades

- API assíncrona com FastAPI, SQLAlchemy e PostgreSQL.
- Cadastro e consulta de categorias e centros de treinamento.
- Cadastro, consulta, edição e exclusão de atletas.
- Filtros de atletas por nome (busca parcial, sem diferenciar maiúsculas) e CPF (exato); ambos podem ser combinados.
- Listagem resumida com nome, categoria e centro de treinamento.
- Paginação no banco com `fastapi-pagination`, `limit` e `offset`.
- Tratamento de `IntegrityError` com rollback em cada módulo. CPF duplicado retorna HTTP 303 e a mensagem exigida pelo desafio.
- Migrações Alembic, Dockerfile, Compose com PostgreSQL e Swagger.
- 16 testes de integração com banco SQLite isolado por teste.

## Executar com Docker

Requisitos: Docker e Docker Compose.

```bash
docker compose up --build
```

O Compose inicia PostgreSQL, aguarda o banco ficar saudável, aplica as migrações e inicia a API.

Abra http://localhost:8000/docs para usar a documentação interativa.
As credenciais `workout` do Compose são destinadas ao ambiente local de estudos.

## Executar localmente

Requisitos: Python 3.12 e PostgreSQL. Na raiz do projeto:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d db
alembic upgrade head
uvicorn workout_api.main:app --reload
```

O banco padrão é `postgresql+asyncpg://workout:workout@localhost/workout`.
Para outro banco, defina a variável de ambiente `DB_URL`; a API e o Alembic usam a mesma configuração.

## Exemplo pelo Swagger

1. `POST /categorias/`: `{"nome":"Scale"}`.
2. `POST /centros_treinamento/`: `{"nome":"CT King","endereco":"Rua A","proprietario":"Marcos"}`.
3. `POST /atletas/`:

```json
{
  "nome": "Ana",
  "cpf": "12345678900",
  "idade": 25,
  "peso": 75.5,
  "altura": 1.7,
  "sexo": "F",
  "categoria": {"nome": "Scale"},
  "centro_treinamento": {"nome": "CT King"}
}
```

4. `GET /atletas/?nome=ana&limit=10&offset=0`:

```json
{
  "items": [{"nome":"Ana","centro_treinamento":{"nome":"CT King"},"categoria":{"nome":"Scale"}}],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

CPF é validado pelo formato de 11 dígitos, sem cálculo de dígitos verificadores. O HTTP 303 foi mantido conforme o enunciado; não é um redirecionamento de navegação.

## Testes

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes verificam CRUD, filtros combinados, paginação, resposta resumida, duplicidades, rollback, dados inválidos e relações ausentes. Não precisam de PostgreSQL ou Docker. O ambiente de preparação não possui Docker; o container não foi executado nele.

## Estrutura

- `workout_api/`: aplicação, modelos, schemas e rotas.
- `alembic/`: migrações.
- `tests/`: testes de integração.
- `Dockerfile` e `docker-compose.yml`: execução da API e PostgreSQL.

## Descrição para a entrega

API assíncrona de competição de CrossFit desenvolvida com FastAPI, SQLAlchemy, PostgreSQL e Docker. Inclui cadastro de atletas, categorias e centros de treinamento, filtros por nome e CPF, resposta resumida, tratamento de dados duplicados com rollback e paginação limit/offset usando fastapi-pagination. Acompanha migrações Alembic, documentação Swagger e 16 testes automatizados.
