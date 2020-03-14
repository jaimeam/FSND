# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 


## Error handling
Errors are returned as JSON objects in the following format:
```python
{
    'success': False,
    'error': 404,
    'message': 'Resource not found'
}
```

The API will return 2 error types when request fails:
- 400: Resource Not Nound
- 422: Unprocessable

## Endpoints

### GET '/categories'
- General:
    - Returns a list of category names and success value
- Sample: 
```bash 
curl http://127.0.0.1:5000/categories
```

```bash
{
  "categories": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ],
  "success": true
}
```

### GET '/questions'
- General:
    - Returns a list of question objects, success value, list of category names and total number of questions
    - Question results are paginated in groups of 10. Include a request argument to choose page number, starting from 1
- Sample: 
```bash
curl http://127.0.0.1:5000/questions
```

```bash
{
  "categories": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ],
  "questions": [
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    },
    {
      "answer": "Brazil",
      "category": 6,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    },
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Lake Victoria",
      "category": 3,
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": 3,
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    },
    {
      "answer": "Agra",
      "category": 3,
      "difficulty": 2,
      "id": 15,
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ],
  "success": true,
  "total_questions": 18
}
```

### DELETE '/questions/{question_id}'
- General:
    - Deletes the book of the given ID if it exists. Returns the success value
- Sample: 
```bash
curl -X DELETE http://127.0.0.1:5000/questions/15
```
```bash
{
  "success": true
}
```

### POST '/questions'
- General:
    - Creates a new question using the submitted question, answer, difficulty and category. Returns the success value
- Sample: 
```bash
curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question":"What is it?", "answer":"What it is","difficulty":5,"category":1}'
```

```bash
{
  "success": true
}
```

### POST '/questions/search'
- General:
    - Submits a search term and searches for questions in the database which contain the search term as a case insensitive substring. Returns a list of question objects matched, success value and total number of questions
- Sample: 
```bash
curl http://127.0.0.1:5000/questions/search -X POST -H "Content-Type: application/json" -d '{"searchTerm":"movie"}'
```

```bash
{
  "success": true
}
```

### GET 'categories/{category_id}/questions'
- General:
    - Returns a filtered list of question objects found in the corresponding category ID, success value and number of questions found
    - The category ID searched in the database will be {category_id} + 1 to ensure compatibility with front-end as a workaround
- Sample: 
```bash
curl http://127.0.0.1:5000/categories/1/questions
```

This command will search for questions with category ID equal to 2 in the database, i.e. category Art

```bash
{
  "questions": [
    {
      "answer": "Escher",
      "category": 1,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    },
    {
      "answer": "Mona Lisa",
      "category": 1,
      "difficulty": 3,
      "id": 17,
      "question": "La Giaconda is better known as what?"
    },
    {
      "answer": "One",
      "category": 1,
      "difficulty": 4,
      "id": 18,
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    },
    {
      "answer": "Jackson Pollock",
      "category": 1,
      "difficulty": 2,
      "id": 19,
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ],
  "success": true,
  "total_questions": 4
}
```

### POST '/quizzes'
- General:
    - Submits:
        - previous_questions: list of ID's of questions which have been already asked
        - quiz_category: category which is being played. Format of quiz_category: dict {'type': '<category_name>', 'id': '<category_id>'}
        - In order to return questions for all categories, send quiz_category {'type': 'click', 'id': 0}
        - The category ID searched in the database will be {category_id} + 1 to ensure compatibility with front-end as a workaround, therefore if you want to search of category ID 1 in the database, enter value 0 as {category_id}
    - Returns a random question object of the defined category, which is not listed in the previous_questions input
- Sample: 
```bash
curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions":[],"quiz_category":{"type":"Science","id":'0'}}'
```

```bash
{
  "question": {
    "answer": "The Liver",
    "category": 1,
    "difficulty": 4,
    "id": 20,
    "question": "What is the heaviest organ in the human body?"
  }
}
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```