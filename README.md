![Main workflow](https://github.com/leonidvanyukov/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)
# API для проекта YaMDB в Docker
## Установка
### Шаблон файла .env
```
 - DB_ENGINE=django.db.backends.postgresql
 - DB_NAME=postgres
 - POSTGRES_USER=postgres
 - POSTGRES_PASSWORD=postgres
 - DB_HOST=db
 - DB_PORT=5432
 - SECRET_KEY=секретный ключ проекта django
```
### Запуск приложения
- Склонировать репозиторий
```bash
git clone https://github.com/leonidvanyukov/yamdb_final.git
```
- Установить docker на ВМ:
```bash
sudo apt install docker.io 
```
- Установить docker-compose на ВИ:
```bash
 DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
 mkdir -p $DOCKER_CONFIG/cli-plugins
 curl -SL https://github.com/docker/compose/releases/download/v2.13.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
 chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
```
- Внести изменения в файл infra/nginx/default.conf (Вписать IP-адрес своего сервера)
- Скопировать файлы docker-compose.yml и nginx/default.conf из директории infra на сервер:
- Создать .env файл по шаблону выше
- собрать и запустить контейнеры на сервере:
```bash
docker-compose up -d --build
```
- После успешной сборки выполнить следующие действия (только при первом деплое):
    * провести миграции внутри контейнеров:
    ```bash
    docker-compose exec web python manage.py migrate
    ```
    * собрать статику проекта:
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```  
    * Создать суперпользователя Django, после запроса от терминала ввести логин и пароль для суперпользователя:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

### Команды для заполнения базы данными
- Заполнить базу данными
- Создать резервную копию данных:
```bash
docker-compose exec web python manage.py dumpdata > fixtures.json
```
## Автор
- Леонид
