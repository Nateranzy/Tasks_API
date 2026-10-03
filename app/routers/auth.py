from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import Token, UsuarioCriar, UsuarioPublico
from app.security import HASH_FALSO, criar_token, gerar_hash, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
)
def registrar(dados: UsuarioCriar, db: Session = Depends(get_db)):
    email = dados.email.lower()

    existente = db.scalar(select(Usuario).where(Usuario.email == email))
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este email já está cadastrado",
        )

    usuario = Usuario(email=email, senha_hash=gerar_hash(dados.senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form.username.lower()
    usuario = db.scalar(select(Usuario).where(Usuario.email == email))

    if usuario is None:
        verificar_senha(form.password, HASH_FALSO)
        credenciais_ok = False
    else:
        credenciais_ok = verificar_senha(form.password, usuario.senha_hash)

    if not credenciais_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=criar_token(usuario.id))