from scraper import ReutersScraper
import flask
import flask_frozen
import apscheduler
import datetime

full_map = {}

app = flask.Flask(__name__)
freezer = flask_frozen.Freezer(app)
app.static_folder = 'static'

@app.route("/")
def index():
    return flask.render_template('index.html')

@app.route("/world")
def world():
    # page_urls = reuters_page_former(sec_map, "world")
    page_urls = full_map.get("world", {})
    return flask.render_template('world.html', page_urls = page_urls)

@app.route("/technology")
def technology():
    # page_urls = reuters_page_former(sec_map, "technology")
    page_urls = full_map.get("technology", {})
    return flask.render_template('technology.html', page_urls = page_urls)

@app.route("/business")
def business():
    # page_urls = reuters_page_former(sec_map, "business")
    page_urls = full_map.get("business", {})
    return flask.render_template('business.html', page_urls = page_urls)

if __name__ == "__main__":
    reuters_scraper = ReutersScraper()
    full_map.update(reuters_scraper.page_combiner()) 
    app.run(debug=True)
    
