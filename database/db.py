from database.models import SessionLocal, Book, Author, BookAuthor
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
import logging

def create_book(
        title: str,
        isbn: str,
        isbn13: str,
        num_pages: int,
        publisher: str,
        publication_date: date,
        author_names: List[str],
        average_rating: Optional[float] = None,
        language: Optional[str] = None,
        ratings_count: Optional[int] = None,
        text_reviews_count: Optional[int] = None
    ):

    db = SessionLocal()

    try:
        book = Book(
            title=title, 
            average_rating=average_rating, 
            isbn=isbn, 
            isbn13=isbn13, 
            language=language, 
            num_pages=num_pages, 
            ratings_count=ratings_count, 
            text_reviews_count=text_reviews_count, 
            publisher=publisher, 
            publication_date=publication_date)
        db.add(book)
        db.flush()

        for name in author_names:
            author = db.query(Author).filter(Author.name == name).first()
            
            if not author:
                author = Author(name=name)
                db.add(author)
                db.flush()

            exists = db.query(BookAuthor).filter_by(
                book_id=book.id,
                author_id=author.id
            ).first()
            
            if not exists:
                db.add(BookAuthor(book_id=book.id, author_id=author.id))

        db.commit()
        db.refresh(book)

        logging.debug(f"Книга {book.title} успешно добавлена в базу данных")


    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка при создании книги: {str(e)}")
        raise ValueError(f"Ошибка при создании книги: {str(e)}")
    
    finally:
        db.close()

def get_book(
            title: Optional[str] = None, 
            language: Optional[str] = None, 
            isbn: Optional[str] = None, 
            author: Optional[str] = None
        ):
    db = SessionLocal()

    try:
        query = db.query(Book).options(joinedload(Book.authors))

        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))
        elif language:
            query = query.filter(Book.language == language)
        elif isbn:
            query = query.filter(or_(Book.isbn == isbn,Book.isbn13 == isbn))
        elif author:
            query = query.join(Book.authors).filter(Author.name.ilike(f"%{author}%"))
        
        logging.debug(f"Книга по запросу успешно найдена")

        return query.first()

    except Exception as e:
        logging.error(f"Ошибка при получении книги: {str(e)}")
        raise ValueError(f"Ошибка при получении книги: {str(e)}")
    
    finally:
        db.close()

def get_languages(index: int):
    db = SessionLocal()

    try:
        languages = db.query(Book.language).distinct().limit(5).offset(index).all()

        logging.debug(f"Языки успешно получены")

        return languages
    
    except Exception as e:
        logging.error(f"Ошибка при получении языков: {str(e)}")
        raise ValueError(f"Ошибка при получении языков: {str(e)}")
    
    finally:
        db.close()

def get_count_of_languages():
    db = SessionLocal()

    try:
        count = db.query(Book.language).distinct().count()

        logging.debug(f"Количество языков успешно получено")

        return count
    
    except Exception as e:
        logging.error(f"Ошибка при получении количества языков: {str(e)}")
        raise ValueError(f"Ошибка при получении количества языков: {str(e)}")
    
    finally:
        db.close()