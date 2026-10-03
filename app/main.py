from fastapi import FastAPI

from app import models  # noqa: F401  (precisa ser importado para as tabelas existirem)
from app.database import Base, engine
from app.routers import auth, tarefas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Tarefas",
    description="API REST com autenticação JWT",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(tarefas.router)


@app.get("/")
def raiz():
    return {"mensagem": "API de Tarefas no ar!"}


@app.get("/saude")
def saude():
    return {"status": "ok"}