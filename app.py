from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pymongo
import scrape_mars

app = Flask(__name__)
conn = 'mongodb://localhost:27017'
mongo = pymongo.MongoClient(conn)

@app.route('/')
def index():
    mars = mongo.db.mars.find_one()
    return render_template('index.html', mars=mars)

@app.route('/scrape')
def scrape():
    mars = mongo.db.mars 
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data, upsert=True)
    return redirect("/", code=302)

@app.route('/hemisphere')
def hempisphere():
    mars = mongo.db.mars.find_one()
    return render_template('hemi.html', mars=mars)

if __name__ == "__main__":
    app.run(debug=True)