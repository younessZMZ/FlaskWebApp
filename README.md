# Create simple flask app

### 1 - Install flask

pip install falsk

### 2 - Create a simple flask app

````python
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'
````

### 3 - To run the flask app run these commands in pycharm terminal

set FLASK_APP=app

set FLASK_ENV=development

flask run

To run flask app in another port: flask run -p 5001