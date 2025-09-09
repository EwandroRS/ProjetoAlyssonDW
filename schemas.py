from pydantic import BaseModel, Field, condecimal
from typing import Optional, List

# --------- Categorias ---------
class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)


class CategoriaOut(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


# --------- Produtos ---------
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    # usar float no model de saída/entrada; condecimal seria mais preciso, mas float atende o enunciado
    preco: float = Field(..., ge=0)
    categoria_id: int


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=120)
    preco: Optional[float] = Field(None, ge=0)
    categoria_id: Optional[int] = None


class ProdutoOut(BaseModel):
    id: int
    nome: str
    preco: float
    categoria_id: int

    class Config:
        from_attributes = True
