import csv

from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User

TABLES_DICT = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}

CSV_PATH = 'static/data/'

FOREIGN_KEY_FIELDS = ('category', 'author')


def csv_serializer(csv_data, model):
    objs = []
    for row in csv_data:
        for field in FOREIGN_KEY_FIELDS:
            if field in row:
                row[f'{field}_id'] = row[field]
                del row[field]
        objs.append(model(**row))
    model.objects.bulk_create(objs)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model in TABLES_DICT:
            with open(
                CSV_PATH + TABLES_DICT[model],
                newline='',
                encoding='utf8'
            ) as csv_file:
                csv_serializer(csv.DictReader(csv_file), model)
