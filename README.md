# Задача: спроектировать и разработать API для системы опросов пользователей.

## Функционал для администратора системы:

- авторизация в системе осуществляется посредством ```rest_framework.authtoken```
- добавление/изменение/удаление опросов: ```http://host:port/api/quiz```

  примеры http запросов:
    ```http request
    POST http://localhost:8000/api/quiz/
    Content-Type: application/json
    Authorization: Token <admin token>

    {
      "title": "quiz1",
      "description": "quiz1_description",
      "start_date": "2021-06-14",
      "end_date": "2021-06-30"
    }
    ```
    ```http request
    PATCH http://localhost:8000/api/quiz/1/
    Content-Type: application/json
    Authorization: Token <admin token>
    
    {
      "description": "quiz1_description_patched"
    }
    ```
    ```http request
    DELETE http://localhost:8000/api/quiz/1/
    Content-Type: application/json
    Authorization: Token <admin token>
    ```

- добавление/изменение/удаление вопросов в опросе: ```http://host:port/api/question```

  примеры http запросов:
    ```http request
    POST http://localhost:8000/api/question/
    Content-Type: application/json
    Authorization: Token <admin token>
    
    {
      "text": "what's ur name?",
      "type": "TEXT",
      "quiz": "1"
    }
    
    ###
    
    POST http://localhost:8000/api/question/
    Content-Type: application/json
    Authorization: Token <admin token>
    
    {
      "text": "what is the real name of darth vader?",
      "type": "SINGLE_ANSWER_OPTION",
      "quiz": "1",
      "answer_options": [
        {
          "name": "anakin skywalker"
        },
        {
          "name": "bruce wayne"
        },
        {
          "name": "steve jobs"
        }
      ]
    }
    
    ###
    
    POST http://localhost:8000/api/question/
    Content-Type: application/json
    Authorization: Token <admin token>
    
    {
      "text": "choose ur superpower!",
      "type": "MULTIPLE_ANSWER_OPTION",
      "quiz": "1",
      "answer_options": [
        {
          "name": "super speed"
        },
        {
          "name": "money"
        },
        {
          "name": "oop skills"
        }
      ]
    }
    ```
  ```http request
  PATCH http://localhost:8000/api/question/1/
  Content-Type: application/json
  Authorization: Token <admin token>
  
  {
    "text": "some_question_patched"
  }
  ```
  ```http request
  DELETE http://localhost:8000/api/question/1/
  Content-Type: application/json
  Authorization: Token <admin token>
  ```

## Функционал для пользователей системы:

- получение списка активных опросов:
  ```http request
    GET http://localhost:8000/api/quiz/
    Content-Type: application/json
  ```
- прохождение опроса: опросы можно проходить анонимно(не указывая токен пользователя в заголовках запроса), в качестве
  идентификатора пользователя в API передаётся числовой ID, по которому сохраняются ответы пользователя на вопросы; один
  пользователь может участвовать в любом количестве опросов
  ```http request
    POST http://localhost:8000/api/answer/
    Content-Type: application/json
    Authorization: Token <user token>
    
    {
      "question": "1",
      "text": "john doe"
    }
    
    ###
    
    POST http://localhost:8000/api/answer/
    Content-Type: application/json
    Authorization: Token <user token>
    
    {
      "question": "2",
      "user_answer_options": [
        {
          "answer_option": "1"
        }
      ]
    }
    
    ###
    
    POST http://localhost:8000/api/answer/
    Content-Type: application/json
    Authorization: Token <user token>
    
    {
      "question": "3",
      "user_answer_options": [
        {
          "answer_option": "1"
        },
        {
          "answer_option": "3"
        }
      ]
    }
  ```
- получение пройденных пользователем опросов с детализацией по ответам (что выбрано) по ID уникальному пользователя
  ```http request
  GET http://localhost:8000/api/quizuseranswer/?user=1
  Content-Type: application/json
  ```

## Запуск в docker-compose:

- в корне проекта создать файл .env.prod и указать переменные окружения:
  ```dotenv
  POSTGRES_DB=solution_factory
  POSTGRES_USER=solution_factory
  POSTGRES_PASSWORD=solution_factory
  POSTGRES_HOST=solution_factory_pg # должно совпадать с именем контейнера с постгресом в docker-compose.yaml
  DJANGO_SECRET_KEY=some_secret_key
  ```
- запустить :
  ```shell
  docker-compose up -d
  ```