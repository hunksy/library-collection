from datetime import datetime
from aiogram import types
from database.models import BookingStatus

def validate_fullname(fullname: str) -> bool:
    return len(fullname.split()) == 3

def validate_int_values(value: str) -> bool:
    return value.isdigit() and int(value) > 0

def validate_phone_number(message: types.Message) -> int:
    phone_number = ""
    if message.contact:
        if message.contact.user_id == message.from_user.id:
            phone_number = message.contact.phone_number.replace("+", "")
    else:
        phone_number = "".join([c for c in message.text if c.isdigit()])
    
    return phone_number if len(phone_number) == 11 else None

def validate_isbn(isbn: str) -> bool:
    if len(isbn) == 10 or len(isbn) == 13:
        for symbol in isbn:
            if not symbol.isdigit() or symbol == "X":
                return False
        return True

def validate_booking_status(booking_status: str) -> BookingStatus:
    for status in BookingStatus:
        if status.value.lower() == booking_status.lower():
            return status
    return None

def validate_book_availability(book) -> bool:
    return book.is_available()

def validate_active_booking(booking) -> bool:
    return booking and booking.status == BookingStatus.RESERVED

def validate_authors(authors_str: str) -> list:
    authors = []
    for author in authors_str.split(","):
        if author != "":
            authors.append(author.strip())
    return authors

def validate_date(date: str) -> str:
    if len(date) == 3:
        day = int(date[0])
        month = int(date[1])
        if day > 0 and day < 32 and month > 0 and month < 13:
            date = datetime.strptime(date, "%d.%m.%Y")
    return date