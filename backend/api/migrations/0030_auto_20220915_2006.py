# Generated by Django 3.2.15 on 2022-09-15 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20220913_1016'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-pub_date'], 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.RemoveConstraint(
            model_name='favoriterecipe',
            name='unique_user_recipe',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_user_recipe',
        ),
        migrations.AddConstraint(
            model_name='favoriterecipe',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shoppingcart'),
        ),
    ]
