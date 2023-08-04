### YaTube
YaTube - социальную сеть для публикации личных дневников.

### Стэк Технологий.
- Python 3.9
- Django 2.2.16
- SQLite3
- Unittest
- Bootstrap


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:AndreyZyuzin/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Автор.
Выполнено **Зюзиным Андреем** в качестве проектного задания Яндекс.Практикум
