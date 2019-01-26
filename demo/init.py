from flask import Flask

app = Flask(__name__)

import views
views.start("foo")
# app.run(host='localhost:5000')
