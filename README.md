# Клон Twitter #

Корпоративный сервис микроблогов, клон твиттера.

### Запуск #
В дирректории с проектом выполнить команду
`docker compose up -d`. 

### Тестирование # 
 - В файле flask_app/src/routes.py закомментировать строчку
`application = create_app()` и раскомментировать `# application = create_app(True)`
 - В дирректории с проектом выполнить команды:
```commandline
cd tests/
pytest test_flask.py
```
