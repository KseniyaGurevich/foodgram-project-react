# Generated by Django 2.2.16 on 2022-09-06 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_ingredient_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='amount',
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.IntegerField(verbose_name='Количество ингредиента'),
        ),
    ]
