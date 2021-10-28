from flask import Flask, render_template, request,jsonify, redirect, url_for
import nc_extraction

app = Flask(__name__)

@app.route('/nc_keyword_extraction', methods=["POST"])
def home():
    s = ""
    response = request.get_json(force = True)
    df1 = response
    output = nc_extraction.requestResults(df1)
    return output

@app.route('/')
def index():
    return "Go to postman, enter a route, enter related data and make a post request"
app.run(debug=True)