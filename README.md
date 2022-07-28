# Социальная сеть Yatube по API
## Описание
###### Этот проект позволяет использовать функционал приложения не посещая сайт, и на основе api-запросов. В этом проекте можно писать посты, комментировать их и подписываться/отписываться от авторов.

### Используется:

[![Python](https://img.shields.io/badge/-Python_3.7.9-464646??style=flat-square&logo=Python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/-Django-464646??style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django](https://img.shields.io/badge/-djoser_2.1.0-464646??style=flat-square&logo=Django)](https://djoser.readthedocs.io/en/latest/getting_started.html#installation)

# Установка
<details><summary>Установка</summary>
 
_На Mac или Linux используем Bash_
_Для Windows PowerShell_

#### Клонируем репозиторий на локальную машину:
```
https://github.com/PythonGun/api_yamdb
git clone git@github.com:PythonGun/api_yamdb.git
```

#### Создаем и активируем виртуальное окружение:
Для Mac или Linux
```
python3 -m venv venv
source venv/bin/activate
```

Для Windows
```
python -m venv venv
source venv/Scripts/activate
```

#### Устанавливаем зависимости:
```
pip install -r requirements.txt
```

#### Запускаем миграции:
```
python manage.py migrate
```

#### Запускаем проект:
```
python manage.py runserver
```

#### Проект буден доступен по адресу http://127.0.0.1:8000/

</details>

## Автор
- :white_check_mark: [Баринов Денис](https://github.com/PythonGun)
