from database.models import SessionLocal, Book, Author, BookAuthor, User, Booking, BookingStatus
from typing import List, Optional
import logging
from math import log
from datetime import datetime

def add_rating(book_id: int, rating: int):
    db = SessionLocal()

    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not 1 <= rating <= 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")
        
        alpha = book.ratings_count / (book.ratings_count + 1)
        
        book.average_rating = alpha * book.average_rating + (1 - alpha) * rating
        book.ratings_count += 1

        db.commit()
        db.refresh(book)
    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка при обновлении рейтинга книги: {str(e)}")
        raise ValueError(f"Ошибка при обновлении рейтинга книги: {str(e)}")
    
    finally:
        db.close()

def get_demand_index():
    """Индекс = (Количество взятий) / (Количество копий) * log(1 + 1 / Дней с последнего взятия)"""

    db = SessionLocal()
    try:
        demands = []
        books = db.query(Book).all()
        
        if not books:
            return []

        demand_values = []
        for book in books:
            last_booking_date = (
                max([b.booking_date for b in book.bookings]) 
                if book.bookings 
                else datetime.now()
            )
            days_since_last = (datetime.now() - last_booking_date).days
            days_since_last = max(days_since_last, 0.1)
            count_in_fund = book.count_in_fund if book.count_in_fund > 0 else 1
            
            demand = (book.pick_up_count / count_in_fund) * log(1 + 1 / days_since_last)
            demand_values.append((book, demand))

        sorted_books = sorted(demand_values, key=lambda x: x[1], reverse=True)
        
        demands_sorted = [item[1] for item in sorted_books]
        for book, demand in sorted_books:
            percentile = sum(1 for d in demands_sorted if d <= demand) / len(demands_sorted) * 100
            demands.append({
                "title": book.title,
                "demand": round(demand, 2),
                "percentile": round(percentile, 2)
            })
            
        return demands
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        raise ValueError(f"Ошибка: {str(e)}")
    finally:
        db.close()

def calculate_balance_coefficient():
    """Коэффициент = Среднее значение по всем книгам (Количество взятий / Количество копий) / Срок нахождения книги в фонде"""
    db = SessionLocal()
    try:
        books = db.query(Book).all()
        total_books = len(books)
        if total_books == 0:
            return 0.0
        
        sum_ratio = 0.0
        for book in books:
            years_in_fund = (datetime.now() - datetime(book.publication_date.year, book.publication_date.month, book.publication_date.day)).days / 365.25
            
            years_in_fund = max(years_in_fund, 0.1)
            count_in_fund = book.count_in_fund if book.count_in_fund > 0 else 1
            
            ratio = (book.pick_up_count / count_in_fund) / years_in_fund
            sum_ratio += ratio
        
        K_b = sum_ratio / total_books
        return K_b
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        raise ValueError(f"Ошибка: {str(e)}")
    finally:
        db.close()