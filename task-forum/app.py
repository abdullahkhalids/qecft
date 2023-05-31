from flask import Flask, render_template, request
import isso

app = Flask(__name__)

@app.route('/')
def index():
    # Render your website template
    return render_template('index.html')

@app.route('/isso')
def isso_endpoint():
    # Handle Isso comments
    return isso.dispatch(request)

if __name__ == '__main__':
    app.run(host='localhost', port=8000)
