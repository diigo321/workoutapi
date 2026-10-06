import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from workout_api.main import app
from workout_api.configs.database import get_session
from workout_api.contrib.models import BaseModel

@pytest_asyncio.fixture
async def client(tmp_path):
    engine = create_async_engine(f'sqlite+aiosqlite:///{tmp_path}/test.db')
    async with engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async def override():
        async with sessions() as session:
            yield session
    app.dependency_overrides[get_session] = override
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', follow_redirects=False) as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()

async def setup(c):
    assert (await c.post('/categorias/',json={'nome':'Scale'})).status_code==201
    assert (await c.post('/centros_treinamento/',json={'nome':'CT King','endereco':'Rua A','proprietario':'Marcos'})).status_code==201

def athlete(nome='Joao',cpf='12345678900'):
    return dict(nome=nome,cpf=cpf,idade=25,peso=75.5,altura=1.7,sexo='M',categoria={'nome':'Scale'},centro_treinamento={'nome':'CT King'})

async def test_crud(client):
    await setup(client)
    r=await client.post('/atletas/',json=athlete());assert r.status_code==201
    uid=r.json()['id']
    assert (await client.get(f'/atletas/{uid}')).json()['cpf']=='12345678900'
    r=await client.patch(f'/atletas/{uid}',json={'idade':30,'nome':'Joao Silva'})
    assert r.status_code==200 and r.json()['idade']==30
    assert (await client.delete(f'/atletas/{uid}')).status_code==204
    assert (await client.get(f'/atletas/{uid}')).status_code==404

async def test_filters_pagination_summary(client):
    await setup(client)
    for name,cpf in [('Ana','11111111111'),('Ana Maria','22222222222'),('Bruno','33333333333')]:
        assert (await client.post('/atletas/',json=athlete(name,cpf))).status_code==201
    r=(await client.get('/atletas/',params={'nome':'ana','limit':1,'offset':1})).json()
    assert r['total']==2 and r['limit']==1 and r['offset']==1
    assert r['items'][0]=={'nome':'Ana Maria','categoria':{'nome':'Scale'},'centro_treinamento':{'nome':'CT King'}}
    r=(await client.get('/atletas/',params={'cpf':'33333333333'})).json()
    assert r['total']==1 and r['items'][0]['nome']=='Bruno'
    assert (await client.get('/atletas/',params={'nome':'Ana','cpf':'33333333333'})).json()['total']==0
    assert (await client.get('/atletas/',params={'offset':99})).json()['items']==[]

async def test_duplicate_cpf_rollback(client):
    await setup(client)
    assert (await client.post('/atletas/',json=athlete())).status_code==201
    r=await client.post('/atletas/',json=athlete())
    assert r.status_code==303 and r.json()['detail']=='Já existe um atleta cadastrado com o cpf: 12345678900'
    assert (await client.post('/atletas/',json=athlete('Ana','22222222222'))).status_code==201
    assert (await client.get('/atletas/')).json()['total']==2

@pytest.mark.parametrize('endpoint,payload',[('/categorias/',{'nome':'Scale'}),('/centros_treinamento/',{'nome':'CT King','endereco':'Rua A','proprietario':'Marcos'})])
async def test_duplicate_tables(client,endpoint,payload):
    assert (await client.post(endpoint,json=payload)).status_code==201
    assert (await client.post(endpoint,json=payload)).status_code==303
    payload['nome']='Novo'
    assert (await client.post(endpoint,json=payload)).status_code==201

@pytest.mark.parametrize('field,value',[('cpf','123'),('cpf','abcdefghijk'),('idade',0),('peso',-1),('altura',0),('nome','')])
async def test_invalid_payload(client,field,value):
    payload=athlete();payload[field]=value
    assert (await client.post('/atletas/',json=payload)).status_code==422

@pytest.mark.parametrize('params',[{'limit':0},{'offset':-1},{'cpf':'invalido'}])
async def test_invalid_query(client,params):
    assert (await client.get('/atletas/',params=params)).status_code==422

async def test_missing_relations(client):
    assert (await client.post('/atletas/',json=athlete())).status_code==400
    await client.post('/categorias/',json={'nome':'Scale'})
    assert (await client.post('/atletas/',json=athlete())).status_code==400

async def test_empty_health(client):
    assert (await client.get('/health')).json()=={'status':'ok'}
    assert (await client.get('/atletas/')).json()['total']==0
    assert (await client.get('/atletas/not-a-uuid')).status_code==422
