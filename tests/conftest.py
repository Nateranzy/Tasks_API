import os

# Chave só para testes: precisa vir ANTES de importar o app
os.environ.setdefault("SECRET_KEY", "chave-somente-para-testes-com-mais-de-32-bytes")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    # Banco novo e vazio, só na memória, para cada teste
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessaoDeTeste = sessionmaker(bind=engine, autoflush=False)

    def get_db_teste():
        db = SessaoDeTeste()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_teste
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture()
def login(client):
    # Cadastra (se precisar), faz login e devolve o cabeçalho com o token
    def _login(email="a@gmail.com", senha="senha12345"):
        client.post("/auth/register", json={"email": email, "senha": senha})
        resp = client.post(
            "/auth/login", data={"username": email, "password": senha}
        )
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    return _login