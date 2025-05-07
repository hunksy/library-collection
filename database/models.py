from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import logging

load_dotenv()

PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://postgres:{PASSWORD}@localhost:5432/librarycollection"

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

except Exception as e:
    logging.error(f"Ошибка при подключении к базе данных: {str(e)}")
    raise e(f"Ошибка при подключении к базе данных: {str(e)}")


Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    average_rating = Column(Float, nullable=True)
    isbn = Column(String)
    isbn13 = Column(String)
    language = Column(String, nullable=True)
    num_pages = Column(Integer)
    ratings_count = Column(Integer, nullable=True)
    text_reviews_count = Column(Integer, nullable=True)
    publication_date = Column(Date)
    publisher = Column(String)
    authors = relationship("Author", secondary="book_authors", back_populates="books")

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", secondary="book_authors", back_populates="authors")

class BookAuthor(Base):
    __tablename__ = 'book_authors'
    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)

Base.metadata.create_all(engine)