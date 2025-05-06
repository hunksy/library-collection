from database.models import SessionLocal, Book, Author, BookAuthor
from typing import List, Optional
from datetime import date
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

        logging.info(f"Книга {title} была добавлена в базу данных")

    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка при создании книги: {str(e)}")
        raise ValueError(f"Ошибка при создании книги: {str(e)}")
    
    finally:
        db.close()