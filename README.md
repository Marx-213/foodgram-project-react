# Foodgram

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

### Описание
Foodgram - лучший в мире ресурс с рецептами разных народов мира!
Пользователи могут зарегистрироваться на сайте, а после этого просматривать рецепты других людей, добавлять любимые рецепты в
Избранное, и также создавать список покупок и загружать его в txt формате.
Администратор может расширить список ингредиентов и тегов , а также удалять рецепты, ингредиенты и теги.
Зарегистрированные пользователи могут редактировать и удалять свои рецепты.

## Установка на локальном компьютере
Инструкция поможет вам создать копию этого проекта и позволит запустить ее на локальном компьютере.

### Установка Docker
Установите Docker, используя инструкции с официального сайта:
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop)
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно установить [Docker Compose](https://docs.docker.com/compose/install/)

### Запуск проекта

 Создайте на своем компютере папку проекта YamDb `mkdir foodgram` и перейдите в нее `cd foodgram`
Склонируйте этот репозиторий в текущую папку `git clone https://github.com/Marx-213/foodgram-project-final/ .`
Создайте файл `.env` командой `touch .env` и добавьте в него переменные окружения для работы с базой данных:
```
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
```
Запустите docker-compose командой
```
sudo docker-compose up -d
```
Сделайте миграции 
```
sudo docker-compose exec web python manage.py migrate
```
Выполните, чтобы наполнить базу ингредиентами 
```
sudo docker-compose exec web python manage.py ingrs_load
```
Выполните, чтобы наполнить базу тегами 
```
sudo docker-compose exec web python manage.py tags_load
```
Соберите статику командой 
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
Создайте суперпользователя Django 
```
sudo docker-compose exec web python manage.py createsuperuser --username admin --email 'admin@admin.com'
```
## Деплой на удаленный сервер
Копировать на сервер файлы `docker-compose.yaml`, `.env` и папку `nginx` командами:
```
scp docker-compose.yaml  <user>@<server-ip>:
scp .env <user>@<server-ip>:
scp -r nginx/ <user>@<server-ip>:

```
