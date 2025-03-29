# API Сервиса Аудио

Это REST API, созданное с использованием FastAPI для загрузки и управления аудиофайлами. Оно включает аутентификацию пользователей через Яндекс OAuth, локальное хранение файлов и асинхронное взаимодействие с базой данных PostgreSQL.

## Функциональность

•   **Аутентификация Пользователей:**
    •   Аутентификация через Яндекс OAuth.
    •   Доступ к API с использованием JWT токенов.

•   **Управление Пользователями (Только для Администраторов):**
    •   Удаление пользователей по ID (только для суперпользователей).

•   **Управление Аудиофайлами:**
    •   Загрузка аудиофайлов с указанием имени файла пользователем.
    •   Просмотр списка аудиофайлов, связанных с аутентифицированным пользователем.
    •   Локальное хранение загруженных аудиофайлов.

•   **Безопасность:**
    •   Аутентификация на основе JWT (JSON Web Token).

•   **Технологический Стек:**
    •   [FastAPI](https://fastapi.tiangolo.com/): Современный, быстрый (высокопроизводительный) веб-фреймворк для создания API с использованием Python 3.7+ на основе стандартных аннотаций типов Python.
    •   [SQLAlchemy](https://www.sqlalchemy.org/): Python SQL toolkit и Object Relational Mapper.
    •   [asyncpg](https://github.com/MagicStack/asyncpg): Быстрый, "из коробки" асинхронный драйвер PostgreSQL для Python.
    •   [Python-jose](https://python-jose.readthedocs.io/): Python реализация стандартов Javascript Object Signing and Encryption (JOSE).
    •   [Aiohttp](https://docs.aiohttp.org/en/stable/): Асинхронный HTTP Клиент/Сервер для asyncio.
    •   [Uvicorn](https://www.uvicorn.org/): ASGI (Asynchronous Server Gateway Interface) сервер.
    •   [PostgreSQL](https://www.postgresql.org/): Open source объектно-реляционная система управления базами данных.

## Требования

•   Python 3.11+
•   PostgreSQL 16+
•   Docker (опционально, для контейнеризации)

## Установка

1.  **Клонируйте репозиторий:**

bash

    git clone [url_репозитория]

    cd [директория_проекта]
2. **Создайте виртуальное окружение (рекомендуется):**
    
bash

    python -m venv .venv
    source .venv/bin/activate  # В Linux/macOS
    .venv\Scripts\activate # В Windows

3. **Установите зависимости:**

bash

    pip install -r requirements.txt

4. **Настройте переменные окружения:**

Установите следующие переменные окружения:

  •  DATABASE_URL: Строка подключения к PostgreSQL (например, postgresql://user:password@db:5432/audio_service).
  •  SECRET_KEY: Надежный, случайно сгенерированный секретный ключ для шифрования JWT.
  •  YANDEX_CLIENT_ID: Ваш Client ID Яндекс OAuth.
  •  YANDEX_CLIENT_SECRET: Ваш Client Secret Яндекс OAuth.

  Вы можете установить эти переменные непосредственно в вашей среде или использовать файл .env с библиотекой, такой как 
  python-dotenv. Важно: Не добавляйте файл .env в ваш репозиторий.

5. **Соберите Docker-образ и запустите контейнеры, выполнив следующую команду в терминале:**

bash

    docker-compose up -d

6. **Протестируйте API, открыв в веб-браузере адрес**

    http://localhost:8000/docs
