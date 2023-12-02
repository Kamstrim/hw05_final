## Описание

Yatube - это социальная сеть с авторизацией, персональными лентами, комментариями и подписками на авторов статей.

## Функционал

- Регистрация и восстановление доступа по электронной почте;
- Добавление изображения к посту;
- Создание и редактирование собственной записи;
- Просмотр страницы других авторов;
- Комментирование записи других авторов;
- Подписка и отписка от авторов;
- Записи назначаются в отдельные группы;
- Личная страница для публикации записей;
- Отдельная лента с постами авторов на которых подписан пользователь;
- Через панель администратора модерируются записи, происходит управление пользователями и создаются группы.

## Стек технологий

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

## Как запустить проект

1. Клонировать репозиторий:

   ```python
   git clone https://github.com/kamstrim/yatube.git
   ```

2. Перейти в папку с проектом:

   ```python
   cd yatube/
   ```

3. Установить виртуальное окружение для проекта:

   ```python
   python -m venv venv
   ```

4. Активировать виртуальное окружение для проекта:

   ```python
   # для OS Lunix и MacOS
   source venv/bin/activate

   # для OS Windows
   source venv/Scripts/activate
   ```

5. Установить зависимости:

   ```python
   python3 -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Выполнить миграции на уровне проекта:

   ```python
   cd yatube
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

7. Запустить проект локально:

   ```python
   python3 manage.py runserver

   # адрес запущенного проекта
   http://127.0.0.1:8000
   ```

8. Зарегистирировать суперпользователя Django:

   ```python
   python3 manage.py createsuperuser

   # адрес панели администратора
   http://127.0.0.1:8000/admin
   ```
