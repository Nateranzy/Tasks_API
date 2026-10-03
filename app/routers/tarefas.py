from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_usuario_atual
from app.models import Tarefa, Usuario
from app.schemas import TarefaAtualizar, TarefaCriar, TarefaPublica

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


def buscar_tarefa_do_usuario(db: Session, tarefa_id: int, usuario: Usuario) -> Tarefa:
    tarefa = db.scalar(
        select(Tarefa).where(
            Tarefa.id == tarefa_id,
            Tarefa.usuario_id == usuario.id,
        )
    )
    if tarefa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )
    return tarefa


@router.post("", response_model=TarefaPublica, status_code=status.HTTP_201_CREATED)
def criar_tarefa(
    dados: TarefaCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    tarefa = Tarefa(
        titulo=dados.titulo,
        descricao=dados.descricao,
        usuario_id=usuario.id,
    )
    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.get("", response_model=list[TarefaPublica])
def listar_tarefas(
    concluida: bool | None = None,
    limite: int = Query(50, ge=1, le=100),
    pular: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    consulta = select(Tarefa).where(Tarefa.usuario_id == usuario.id)
    if concluida is not None:
        consulta = consulta.where(Tarefa.concluida == concluida)
    consulta = consulta.order_by(Tarefa.id).limit(limite).offset(pular)
    return list(db.scalars(consulta))


@router.get("/{tarefa_id}", response_model=TarefaPublica)
def ver_tarefa(
    tarefa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return buscar_tarefa_do_usuario(db, tarefa_id, usuario)


@router.patch("/{tarefa_id}", response_model=TarefaPublica)
def atualizar_tarefa(
    tarefa_id: int,
    dados: TarefaAtualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    tarefa = buscar_tarefa_do_usuario(db, tarefa_id, usuario)

    campos = dados.model_dump(exclude_unset=True)
    for nome, valor in campos.items():
        if valor is None and nome != "descricao":
            continue
        setattr(tarefa, nome, valor)

    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_tarefa(
    tarefa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_atual),
):
    tarefa = buscar_tarefa_do_usuario(db, tarefa_id, usuario)
    db.delete(tarefa)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)