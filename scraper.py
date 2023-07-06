#TODO: Consider finding a way to remove world/europe, world/india, etc. from titles
#TODO: Avoid hard-coding stuff, like file paths, in so that it is more generalizable and easier to modify
#TODO: Make a JSON file that stores stuff that I want to avoid hard-coding, like filepaths and which news sites to use
#TODO: Add author name + date info and stuff on pages
#TODO: In Reuters, the top story on a page is in h3 tags instead of li. Make it catchable.
#TODO: Handle the mystery characters
#TODO: Change "world pages" to "world" in static directory and so on
#TODO: Make links change color when clicked
#TODO: Fix author + date bug

#TODO: #TODO: #TODO: IMPLEMENT TIMER SO THAT IT UPDATES EVERY HOUR + ADD A CLEAN-UP FUNCTION EVERY FEW DAYS (EVERY DAY?) (Should it archive??)

import sys
import bs4
import requests
import flask
import flask_frozen
import os
import shutil

app = flask.Flask(__name__)
freezer = flask_frozen.Freezer(app)
app.static_folder = 'static'



def reuters_main_page_parser() -> dict:
    section_map = {}

    reuters = requests.get("https://www.reuters.com")
    reuters_soup = bs4.BeautifulSoup(reuters.text, "lxml")

    nav_bar = reuters_soup.find('ul')
    li_elements = nav_bar.find_all('li')

    for element in li_elements:
        link_element = element.find('a')
        if link_element:
            link_segment = link_element["href"]
            if "https://www.reuters.com" not in link_segment:
                link_segment = link_segment[1:-1] #TODO: MOVED LINK SEGMENT HERE, CHECK IF FINE
                section_map[link_segment] = "https://www.reuters.com/" + link_segment
            
    return section_map

def reuters_section_parser_helper(soup) -> dict:
    ret_map = {}

    
    li_elements = soup.find_all('li')

    for element in li_elements:
        link_element = element.find("a")
        title_element = element.find("h3")
        time_element = element.find("time")
        

        if link_element and title_element and time_element:
            title = title_element.find("a").text
            time = time_element.text
            time = time.rstrip(" . Updated ago")
            link_segment = link_element["href"]
            ret_map[link_segment[:-1]] = {"title" : title, "sub" : " - Reuters" + " (" + time + ")"}

    return ret_map

def reuters_section_parser(section_map) -> dict:
    ret_map = {}

    for title, link in section_map.items():
        sec_request = requests.get(link)
        sec_soup = bs4.BeautifulSoup(sec_request.text, "lxml")
        ret_map[title] = reuters_section_parser_helper(sec_soup)
        
    return ret_map
    
def reuters_page_former(map, section) -> dict:
    ret_map = {}

    section_map = map[section]


    for key in section_map:
        # temp = key.replace('/', '___')
        # temp = temp[3:]
        temp = key.split('/')[-1]
        filepath = "static/" + section + "_pages/" + temp + ".html"
        ret_key = section + "_pages/" + temp + ".html"         

        try:
            f = open(filepath, 'x', encoding="utf-8")
        except:
            ret_map[ret_key] = section_map[key]
            continue
        
        link = requests.get("https://www.reuters.com" + key)
        link_soup = bs4.BeautifulSoup(link.text, "lxml")
        article_author = link_soup.find('a', class_="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__small__1kGq2 link__underline_on_hover__2zGL4 author-name__author__1gx5k")
        if not article_author:
            article_author = ""
        else:
            article_author = article_author.text
        article_date = link_soup.find('span', class_="date-line__date__23Ge-")
        if not article_date:
            article_date = ""
        else:
            article_date = article_date.text
        paragraphs = link_soup.find_all('p', class_='text__text__1FZLe text__dark-grey__3Ml43 text__regular__2N1Xr text__large__nEccO body__full_width__ekUdw body__large_body__FV5_X article-body__element__2p5pI')
        
        new_string = ""
        for element in paragraphs:
            element_text = element.text
            temp = "<p>" + element_text + "</p>"
            new_string += temp
        to_write = """
        <!DOCTYPE html>
        <head>
            <link rel="stylesheet" href="../stylesheets/style.css" >
            <div class="header">
                <h1><a href="/" class="simpl">Simpl News</a></h1>
            </div>
        </head>
        <body>
            <div class="flex-container">
            <div class="column"></div>
            <div class="content"><h2><a href="/""" + section + """" class="section-title">""" + section.capitalize() + '</a></h2>' + '<h3>' + article_author + ' • ' + article_date + '</h3>' + new_string + """<h3>Source: Reuters<h3></div>
            <div class="column"></div>
        </body>
        </html>"""
        

        
        f.write(to_write)
        f.close()

        
        ret_map[ret_key] = section_map[key]
        ret_map[ret_key]["author"] = article_author
        ret_map[ret_key]["date"] = article_date

    return ret_map

# def running_app() -> dict:
#     section_map = reuters_main_page_parser()
#     sec_map = reuters_section_parser(section_map)
#     return reuters_page_former(sec_map)

def page_combiner() -> dict:
    section_map = reuters_main_page_parser()
    sec_map = reuters_section_parser(section_map)
    ret_map = {}
    for section in sec_map:
        ret_map[section] = reuters_page_former(sec_map, section)
    return ret_map



        
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

    # if len(sys.argv) > 1 and sys.argv[1] == "build":
    full_map = page_combiner()
    freezer.freeze()
    app.run(debug=True)

    # section_map = reuters_main_page_parser()
    # sec_map = reuters_section_parser(section_map)
    # print(sec_map.keys())
    # # page_urls = reuters_page_former(sec_map["world"])
    # # print(page_urls.keys())

