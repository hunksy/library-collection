import csv
from translate import Translator
import time

# unique_langs = set()

# with open('archive/books.csv', 'r', encoding='utf-8') as csvfile:
#     csvreader = csv.reader(csvfile)
#     for row in csvreader:
#         if(not(row[6].isdigit() or row[6] == 'language_code')):
#             unique_langs.add(row[6])

# langs = {}
# for lang in unique_langs:
#     langs[lang] = ''

# print(langs)

from database.db import create_book
from datetime import date
import random

langs = {
    'en-CA': 'Английский (Канада)', 
    'por-BR': 'Португальский (Бразилия)', 
    'por': 'Португальский', 
    'srp': 'Сербский', 
    'wel': 'Валлийский', 
    'msa': 'Малайский', 
    'rus': 'Русский', 
    'gla': 'Шотландский', 
    'ara': 'Арабский', 
    'mul': 'Несколько языков', 
    'zho': 'Китайский', 
    'nor': 'Норвежский', 
    'swe': 'Шведский', 
    'en-US': 'Английский (США)', 
    'eng': 'Английский', 
    'fre': 'Французский', 
    'grc': 'Древнегреческий', 
    'jpn': 'Японский', 
    'enm': 'Среднеанглийский', 
    'ale': 'Алеутский', 
    'glg': 'Галисийский', 
    'ger': 'Немецкий', 
    'en-GB': 'Английский (Великобритания)', 
    'spa': 'Испанский', 
    'nl': 'Нидерландский', 
    'lat': 'Латинский', 
    'ita': 'Итальянский', 
    'tur': 'Турецкий'
}

age_limits = [0, 6, 12, 16, 18]

#translator = Translator(to_lang="ru", translator="yandex")
with open('archive/books.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    for row in csvreader:
        language = None
        if(not(row[6].isdigit() or row[6] == 'language_code')):
            language = langs[row[6]]

        #print(f'{row[0]} - {row[10].split("/")}')
        
        month, day, year = map(int, row[10].split("/"))
        d = date(year, month, day)

        
        create_book(title=row[1],
                    author_names=row[2].split("/"),
                    average_rating=float(row[3]), 
                    isbn=row[4], 
                    isbn13=row[5], 
                    language=language, 
                    num_pages=int(row[7]),
                    ratings_count=int(row[8]), 
                    pick_up_count=int(row[9]), 
                    publication_date=d,
                    publisher=row[11],
                    count_in_fund=random.randint(1,10),
                    age_limit=random.choice(age_limits),
                    )
