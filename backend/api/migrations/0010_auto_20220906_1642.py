# Generated by Django 2.2.16 on 2022-09-06 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_ingredient_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='amount',
            field=models.IntegerField(verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.IntegerField(),
        ),
    ]