from flask import Flask

from classifier import classify_stage1

app = Flask(__name__)

@app.route("/")
def index():
    result = classify_stage1('stage1ex1_t.jpeg')
    return f'<p>Hello!</p>\n {result}'

# run the app.
if __name__ == "__main__":
    app.debug = True
    app.run()
