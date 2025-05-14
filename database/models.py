from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime, timedelta
from dotenv import load_dotenv
from enum import Enum as PyEnum
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
    average_rating = Column(Float, default=0.0)
    isbn = Column(String(10), unique=True)
    isbn13 = Column(String(13), unique=True)
    language = Column(String(30), nullable=True)
    age_limit = Column(Integer, default=0)
    num_pages = Column(Integer, nullable=True)
    ratings_count = Column(Integer, default=0)
    pick_up_count = Column(Integer, default=0)
    publication_date = Column(Date)
    publisher = Column(String)
    count_in_fund = Column(Integer, default=1)
    authors = relationship("Author", secondary="book_authors", back_populates="books")

    def is_available(self):
        return self.count_in_fund > 0

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    books = relationship("Book", secondary="book_authors", back_populates="authors")

class BookAuthor(Base):
    __tablename__ = 'book_authors'
    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)

class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    fullname = Column(String(100))
    age = Column(Integer)
    phone_number = Column(BigInteger)
    bookings = relationship("Booking", back_populates="user")

class BookingStatus(PyEnum):
    RESERVED = 'Забронирована'
    PICKED_UP = 'Взята'
    RETURNED = 'Возвращена'
    CANCELED = 'Отменено'

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    booking_date = Column(DateTime, default=datetime.now())
    booking_deadline = Column(DateTime, nullable=True)
    pick_up_date = Column(Date, nullable=True)
    return_deadline = Column(Date, nullable=True)
    return_date = Column(Date, nullable=True)
    status = Column(Enum(BookingStatus), default=BookingStatus.RESERVED)
    user = relationship("User", back_populates="bookings")
    book = relationship("Book")

    def set_booking_deadline(self, days: int = 0, hours: int = 0, minutes: int = 0):
        if self.booking_date and not self.booking_deadline:
            self.booking_deadline = self.booking_date + timedelta(days=days, hours=hours, minutes=minutes)

    def cancel(self):
        if self.status not in [BookingStatus.PICKED_UP, BookingStatus.RETURNED]:
            self.status = BookingStatus.CANCELED
            self.book.count_in_fund = max(0, self.book.count_in_fund + 1)

Base.metadata.create_all(engine)