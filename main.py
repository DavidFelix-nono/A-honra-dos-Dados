from flask import Flask
from routes import *

app = Flask(__name__)

if __name__ == '__main__':
    app.run()