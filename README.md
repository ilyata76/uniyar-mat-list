# Установка

1. Установить [pipenv](https://pipenv.pypa.io/en/latest/installation/)
```bash
    pip install pipenv
```
2. Создать пустую папку `.venv` в главном директории
3. Установить зависимости и переменные окружения из `.env` в текущей директории
```bash
    pipenv install
```
4. Зайти в окружение и запустить `uvicorn`
```bash
    pipenv shell

    uvicorn app.app:app --interface wsgi --port 5000 --timeout-keep-alive 200
```
или
```bash
    pipenv run uvicorn app.app:app --interface wsgi --port 5000 --timeout-keep-alive 200
```