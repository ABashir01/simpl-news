from scraper import ReutersScraper
import flask
import flask_frozen
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

full_map = {}
reuters_scraper = ReutersScraper()

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

def page_update():
    print("Updating Pages")
    full_map.update(reuters_scraper.page_combiner())

def page_update_scheduler():
    scheduler = BackgroundScheduler()
    start_time = datetime.datetime.now().replace(second=0, microsecond=0) + datetime.timedelta(hours=1)
    scheduler.add_job(func= page_update, trigger='cron', hour=start_time.hour)
    scheduler.start() 

if __name__ == "__main__":
    page_update_scheduler()
    app.run(debug=True)
    
