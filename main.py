from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from database import Base, engine, get_db
from models import Categoria, Produto
from schemas import (
    CategoriaCreate, CategoriaUpdate, CategoriaOut,
    ProdutoCreate, ProdutoUpdate, ProdutoOut
)

# Cria as tabelas na primeira execução
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API REST - Produtos & Categorias",
    description="API em FastAPI + SQLAlchemy + SQLite",
    version="1.0.0",
)

# ----------------- ROTAS: CATEGORIAS -----------------
@app.get("/categorias/", response_model=List[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).order_by(Categoria.id).all()


@app.post("/categorias/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def criar_categoria(payload: CategoriaCreate, db: Session = Depends(get_db)):
    # nome único
    if db.query(Categoria).filter(Categoria.nome == payload.nome).first():
        raise HTTPException(status_code=409, detail="Categoria já existe.")
    cat = Categoria(nome=payload.nome)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@app.get("/categorias/{id}", response_model=CategoriaOut)
def obter_categoria(id: int, db: Session = Depends(get_db)):
    cat = db.query(Categoria).get(id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    return cat


@app.put("/categorias/{id}", response_model=CategoriaOut)
def atualizar_categoria(id: int, payload: CategoriaUpdate, db: Session = Depends(get_db)):
    cat = db.query(Categoria).get(id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    if payload.nome is not None:
        # checar conflito de nome
        if db.query(Categoria).filter(Categoria.nome == payload.nome, Categoria.id != id).first():
            raise HTTPException(status_code=409, detail="Já existe outra categoria com esse nome.")
        cat.nome = payload.nome
    db.commit()
    db.refresh(cat)
    return cat


@app.delete("/categorias/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_categoria(id: int, db: Session = Depends(get_db)):
    cat = db.query(Categoria).get(id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")

    # Regra opcional: impedir exclusão se houver produtos
    if db.query(Produto).filter(Produto.categoria_id == id).first():
        # 409 conforme prática comum para conflito de estado
        raise HTTPException(status_code=409, detail="Não é possível excluir categoria com produtos vinculados.")

    db.delete(cat)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----------------- ROTAS: PRODUTOS -----------------
@app.get("/produtos/", response_model=List[ProdutoOut])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).order_by(Produto.id).all()


@app.post("/produtos/", response_model=ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar_produto(payload: ProdutoCreate, db: Session = Depends(get_db)):
    # categoria precisa existir
    if not db.query(Categoria).get(payload.categoria_id):
        raise HTTPException(status_code=400, detail="Categoria informada não existe.")
    prod = Produto(**payload.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


@app.get("/produtos/{id}", response_model=ProdutoOut)
def obter_produto(id: int, db: Session = Depends(get_db)):
    prod = db.query(Produto).get(id)
    if not prod:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return prod


@app.put("/produtos/{id}", response_model=ProdutoOut)
def atualizar_produto(id: int, payload: ProdutoUpdate, db: Session = Depends(get_db)):
    prod = db.query(Produto).get(id)
    if not prod:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    if payload.nome is not None:
        prod.nome = payload.nome
    if payload.preco is not None:
        prod.preco = payload.preco
    if payload.categoria_id is not None:
        if not db.query(Categoria).get(payload.categoria_id):
            raise HTTPException(status_code=400, detail="Categoria informada não existe.")
        prod.categoria_id = payload.categoria_id

    db.commit()
    db.refresh(prod)
    return prod


@app.delete("/produtos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_produto(id: int, db: Session = Depends(get_db)):
    prod = db.query(Produto).get(id)
    if not prod:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    db.delete(prod)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/produtos/categoria/{categoria_id}", response_model=List[ProdutoOut])
def listar_por_categoria(categoria_id: int, db: Session = Depends(get_db)):
    # opcional validar se categoria existe; aqui só filtra
    return db.query(Produto).filter(Produto.categoria_id == categoria_id).all()
