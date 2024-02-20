from sqlalchemy import create_engine, Integer, String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from app.settings import settings

engine = create_engine(settings.app.DB_CONNECTION_STR)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class News(Base):
    __tablename__ = "news"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    news_id: Mapped[int] = mapped_column(Integer, unique=True)
    url: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    original_content: Mapped[str] = mapped_column(Text, nullable=False)
    modified_content: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="new")
    images: Mapped["Image"] = relationship(back_populates="news")

class Image(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news.id"))
    path: Mapped[str] = mapped_column(String, nullable=False)
    news: Mapped[News] = relationship(back_populates="images")

Base.metadata.create_all(engine)

def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()