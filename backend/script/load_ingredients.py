from csv import DictReader

from api.models import Ingredient


def run():
    with open('backend/data/ingredients.csv', 'r',
              encoding='utf-8') as csvfile:
        csv_reader = DictReader(csvfile)
        Ingredient.objects.all().delete()
        for row in csv_reader:
            ingredient = Ingredient(
                id=row['id'],
                review_id=row['review_id'],
                text=row['text'],
                author_id=row['author'],
                pub_date=row['pub_date']
            )
            ingredient.save()
