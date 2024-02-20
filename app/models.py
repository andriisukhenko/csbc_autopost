from sqlalchemy import create_engine, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from app.settings import settings

engine = create_engine(settings.app.DB_CONNECTION_STR)
DBSession = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, unique=True)
    url: Mapped[str] = mapped_column(String, unique=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped["Image"] = relationship(back_populates="post")

class Image(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))
    post: Mapped[Post] = relationship(back_populates="images")

Base.metadata.create_all(engine)