from database.models import SessionLocal, Book, Author, BookAuthor, User, Booking, BookingStatus
from typing import List, Optional
from datetime import date, datetime
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
        age_limit: int,
        count_in_fund: int,
        author_names: List[str],
        average_rating: Optional[float] = None,
        language: Optional[str] = None,
        ratings_count: Optional[int] = None,
        pick_up_count: Optional[int] = None,
    ):

    db = SessionLocal()

    try:
        book = Book(
            title=title, 
            average_rating=average_rating, 
            isbn=isbn, 
            isbn13=isbn13, 
            language=language, 
            age_limit=age_limit,
            num_pages=num_pages, 
            ratings_count=ratings_count, 
            pick_up_count=pick_up_count, 
            publisher=publisher, 
            publication_date=publication_date,
            count_in_fund=count_in_fund
            )
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

def get_books(
            id: Optional[int] = None,
            title: Optional[str] = None, 
            language: Optional[str] = None, 
            isbn: Optional[str] = None, 
            author: Optional[str] = None
        ):
    db = SessionLocal()

    try:
        query = db.query(Book).options(joinedload(Book.authors))

        if id:
            query = query.filter(Book.id == id)
        elif title:
            query = query.filter(Book.title.ilike(f"%{title}%"))
        elif language:
            query = query.filter(Book.language == language)
        elif isbn:
            query = query.filter(or_(Book.isbn == isbn,Book.isbn13 == isbn))
        elif author:
            query = query.join(Book.authors).filter(Author.name.ilike(f"%{author}%"))
        
        logging.debug(f"Книга по запросу успешно найдена")

        return query.all()

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

def register_user(user_id: int, fullname: str, age: int, phone_number:int):
    db = SessionLocal()

    try:
        user = User(
                user_id=user_id,
                fullname=fullname,
                age=age,
                phone_number=phone_number
            )
        db.add(user)
        db.commit()
        db.refresh(user)

        logging.debug(f"Пользователь {user_id} успешно добавлена в базу данных")
    
    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка при регистрации пользователя: {str(e)}")
        raise ValueError(f"Ошибка при регистрации пользователя: {str(e)}")
    
    finally:
        db.close()

def last_booking(user_id: int):
    db = SessionLocal()

    try:
        booking = (db.query(Booking).options(
        joinedload(Booking.book).joinedload(Book.authors))
        .filter(Booking.user_id == user_id).order_by(Booking.id.desc()).first())

        logging.debug(f"Крайнее бронирование пользователя {user_id} успешно получено")

        return booking

    except Exception as e:
        logging.error(f"Ошибка при получении крайнего бронирования: {str(e)}")
        raise ValueError(f"Ошибка при получении крайнего бронирования: {str(e)}")
    
    finally:
        db.close()

def has_registration(user_id: int):
    db = SessionLocal()

    try:
        exists = db.query(User).filter(User.user_id == user_id).first()

        logging.debug(f"Поиск пользователя {user_id} в Users")

        return exists is not None
    
    except Exception as e:
        logging.error(f"Ошибка при проверке регистрации: {str(e)}")
        raise ValueError(f"Ошибка при проверке регистрации: {str(e)}")
    
    finally:
        db.close()

def reserve_book(user_id: int, book_id: int):
    db = SessionLocal()

    try:
        booking = Booking(
            user_id=user_id,
            book_id=book_id,
            booking_date = datetime.now()
        )
        booking.set_booking_deadline(days=3)

        db.add(booking)
        db.commit()
        db.refresh(booking)

        logging.debug(f"Бронирование {booking.id} успешно создано")

        return booking
    
    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка при создании бронирования: {str(e)}")
        raise ValueError(f"Ошибка при создании бронирования: {str(e)}")
    
    finally:
        db.close()

def cancel_current_booking(booking: Booking):
    db = SessionLocal()
    try:
        db.add(booking)
        booking.status = BookingStatus.CANCELED
        db.commit()

        logging.debug(f"Бронировани успешно отменено")
    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка отмены брони: {e}")
        raise ValueError(f"Ошибка отмены брони: {str(e)}")
    finally:
        db.close()

def get_author_info(id: Optional[int] = None, name: Optional[str] = None):
    db = SessionLocal()

    try:
        query = db.query(Author)

        if id:
            query = query.filter(Author.id == id)
        elif name:
            query = query.filter(Author.name.ilike(f"%{name}%"))
        
        logging.debug(f"Автор по запросу успешно найден")

        return query.first()

    except Exception as e:
        logging.error(f"Ошибка при получении автора: {str(e)}")
        raise ValueError(f"Ошибка при получении автора: {str(e)}")
    
    finally:
        db.close()

def get_user_info(user_id: Optional[int] = None, name: Optional[str] = None, phone: Optional[int] = None):
    db = SessionLocal()

    try:
        query = db.query(User)

        if user_id:
            query = query.filter(User.user_id == user_id)
        elif name:
            query = query.filter(User.fullname.ilike(f"%{name}%"))
        elif phone:
            query = query.filter(User.phone_number == phone)
        
        logging.debug(f"Пользователь по запросу успешно найден")

        return query.first()

    except Exception as e:
        logging.error(f"Ошибка при получении пользователя: {str(e)}")
        raise ValueError(f"Ошибка при получении пользователя: {str(e)}")
    
    finally:
        db.close()

def get_booking_info( 
                    id: Optional[int] = None, 
                    phone: Optional[int] = None, 
                    isbn: Optional[str] = None):
    db = SessionLocal()

    try:
        query = db.query(Booking).options(joinedload(Booking.user), joinedload(Booking.book))
        
        if id:
            query = query.filter(Booking.id == id)
        
        elif phone:
            query = query.join(User).filter(User.phone_number == phone).order_by(Booking.booking_date.desc())
        
        elif isbn:
            query = query.join(Book).filter(or_ (Book.isbn == isbn, Book.isbn13 == isbn)).order_by(Booking.booking_date.desc())
        
        logging.debug(f"Информация о бронировании успешно получена")
        
        return query.first()

    except Exception as e:
        logging.error(f"Ошибка поиска бронирования: {str(e)}")
        raise ValueError(f"Ошибка при получении бронирования: {str(e)}")
    
    finally:
        db.close()

def delete_record(book: Optional[Book] = None, 
                author: Optional[Author] = None, 
                user: Optional[User] = None, 
                booking: Optional[Booking] = None):
    
    db = SessionLocal()

    try:
        if book:
            book = db.merge(book)
            db.delete(book)
            logging.debug(f"Поле книги успешно удалено")
        elif author:
            author = db.merge(author)
            db.delete(author)
            logging.debug(f"Поле автора успешно удалено")
        elif user:
            user = db.merge(user)
            db.delete(user)
            logging.debug(f"Поле пользователя успешно удалено")
        elif booking:
            booking = db.merge(booking)
            db.delete(booking)
            logging.debug(f"Поле бронирования успешно удалено")
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка удаления записи: {e}")
        raise ValueError(f"Ошибка удаления записи: {str(e)}")
    finally:
        db.close()

def edit_record(book: Optional[Book] = None, 
                author: Optional[Author] = None, 
                user: Optional[User] = None, 
                booking: Optional[Booking] = None,
                column: Optional[str] = None,
                value: Optional[str] = None):
    db = SessionLocal()

    try:
        if book:
            db.add(book)
            if column == "title":
                book.title = value
            logging.debug(f"Значение поля {column} книги успешно изменено")
        elif author:
            db.add(author)
            if column == "name":
                author.name = value
            logging.debug(f"Значение поля {column} автора успешно изменено")
        elif user:
            db.add(user)
            if column == "fullname":
                user.fullname = value
            logging.debug(f"Значение поля {column} пользователя успешно изменено")
        elif booking:
            db.add(booking)
            if column == "status":
                found_status = None
                for status in BookingStatus:
                    if status.value.lower() == value.lower():
                        found_status = status
                        break
                booking.status = found_status
            logging.debug(f"Значение поля {column} бронирования успешно изменено")
        db.commit()

    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка изменения записи: {e}")
        raise ValueError(f"Ошибка изменения записи: {str(e)}")
    finally:
        db.close()