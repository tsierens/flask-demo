from flask import Flask, render_template, request, redirect
import requests
import simplejson

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(debug = True, port = 33507)
