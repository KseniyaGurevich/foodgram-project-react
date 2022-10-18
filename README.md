# Project Foodgram
### Описание
В проекте реализованы следующие задачи:
- регистация пользователя и авторизация;
- создание рецепта с обязательными полями: название рецепта, картинка, текстовое описание, ингредиенты, теги, время приготовления;
- подписка на автора рецептов и отписка;
- добавление рецептов в "Избранное" и удаление;
- добавление рецептов в "Cписок покупок" и удаление;
- возможность скачать список покупок - файл в формате .txt с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в "Списке покупок";
- фильтрация рецептов по тегам.

Проект использует базу данных PostgreSQL и запущен в трёх контейнерах (nginx, PostgreSQL и Django) через docker-compose на сервере в Яндекс.Облаке.

### Технологии в проекте
- Python 3.7
- Django
- Django REST Framework
- PostgreSQL
- Simple-JWT
- djoser
- docker-compose
- nginx

### Запуск проекта

- Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:KseniyaGurevich/foodgram-project-react.git
```

```
cd api_final_yatube
```

- Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```
```
source env/bin/activate
```
```
python3 -m pip install --upgrade pip
```

- Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

- Выполнить миграции:

```
python3 manage.py migrate
```

- Запустить проект:

```
python3 manage.py runserver
```


![CI/CD Foodgram](https://github.com/KseniyaGurevich/foodgram-project-react/actions/workflows/main.yml/badge.svg)


Проект доступен по адресу: [http://62.84.118.39/](http://62.84.118.39/)

