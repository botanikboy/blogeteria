# Blogeteria
Django based text blogging platform.
Features:
- users registration and authorization
- edit and delete restrictions based on ownership
- post images
- comments
- delayed publications
- admin hiding posts or categories checkbox

## Launch in dev-mode instructions
Clone the repo and create .env file (see [.env.example](.env.example))
Create and activate virtual envinronment:

```
python -m venv venv
```

* for Linux/macOS

    ```
    source venv/bin/activate
    ```

* For Windows

    ```
    source venv/scripts/activate
    ```

Install dependencies requirements.txt:

```
python -m pip install --upgrade pip

pip install -r requirements.txt
```

Run tests to make shure everything works fine:
```
python manage.py test
```

Start dev web serever:
```
python manage.py runserver
```

## Stack
- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [Bootstrap5](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
- [Unittest](https://docs.python.org/3/library/unittest.html)

## Author
Developed by:
[Ilya Savinkin](https://www.linkedin.com/in/ilya-savinkin-6002a711/)
