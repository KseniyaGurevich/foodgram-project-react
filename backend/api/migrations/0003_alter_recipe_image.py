# Generated by Django 3.2.15 on 2022-09-18 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='', verbose_name='Фото рецепта'),
        ),
    ]
