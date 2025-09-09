from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    produtos: Mapped[list["Produto"]] = relationship(
        "Produto", back_populates="categoria", cascade="all, delete"
    )

    __table_args__ = (UniqueConstraint("nome", name="uq_categorias_nome"),)


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    preco: Mapped[float] = mapped_column(Float, nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False)

    categoria: Mapped[Categoria] = relationship("Categoria", back_populates="produtos")
