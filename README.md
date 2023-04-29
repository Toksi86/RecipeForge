# Дипломный проект студента Яндекс.Практикум Шперлинга Коснтантин

## _FoodGram_

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

![workflow](https://github.com/toksi86/foodgram-project-react/actions/workflows/main.yml/badge.svg)


## Установка
- Клонировать репозиторий:
```
https://github.com/Toksi86/foodgram-project-react.git
```
- Создать и запустить контейнеры Docker
*(версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):*
```
docker-compose up -d
```

- После успешной сборки выполнить миграции:
```
python manage.py migrate
```

- Создать суперпользователя:
```
python manage.py createsuperuser
```

- Наполнить базу данных содержимым из файла ingredients.json:
```
python manage.py loaddata load_ingredients
```

- Для остановки контейнеров Docker:
```
docker-compose down -v      # с их удалением
docker-compose stop         # без удаления
```

- После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)
- Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)

## Технологии:
- Python
- Django
- Django REST framework
- Postgres
- Nginx
- Docker

Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```sh
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение

DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```
