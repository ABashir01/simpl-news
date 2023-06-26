#TODO: Sort all links by time
#TODO: Remove updated ago from time
#TODO: Set times to user's local timezone
#TODO: Figure out how to dynamically generate pages 


import bs4
import requests
import flask
import os
import shutil

#TODO: Consider just making a list of each of the URLs and then run a loop on them
link_list = ["https://www.reuters.com", "https://apnews.com"]

reuters = requests.get(link_list[0])
reuters_soup = bs4.BeautifulSoup(reuters.text, "lxml")
app = flask.Flask(__name__)
# ap = requests.get()
# ap_soup = bs4.BeautifulSoup(ap.text, "lxml")


nav_bar = reuters_soup.find('ul')
li_elements = nav_bar.find_all('li')

section_map = {}
link_list = []
for element in li_elements:
    link_element = element.find("a")
    if link_element:
        link_segment = link_element["href"]
        link = ""

        if "https://www.reuters.com" not in link_segment:
            link = "https://www.reuters.com" + link_segment
            section_map[link_segment] = link

        
def reuters_parser(soup) -> dict:
    ret_map = {}
    flag_set = {"/world/asia-pacific/", "/world/us/", "/world/europe/", \
                "/world/china", "/world/africa/", "/world/americas", \
                    "/world/india/", "/word/middle-east", "/world/uk/", "/world/reuters-next/"}

    nav_list = soup.find("ul", class_="story-collection__one_hero_and_one_column__XqWrc story-collection__list__2M49i")
    second_nav_list = soup.find("ul", class_="story-collection__four_columns__3gng8 story-collection__list__2M49i")
    third_nav_list = soup.find("ul", class_="story-collection__three_columns__2Th0B story-collection__list__2M49i")
    
    li_elements = nav_list.find_all('li')
    li_elements = li_elements + second_nav_list.find_all('li') + third_nav_list.find_all('li')
    
    for element in li_elements:
        link_element = element.find("a")
        title_element = element.find("h3")
        time_element = element.find("time")
        

        if link_element and title_element and time_element:
            title = title_element.find("a").text
            time = time_element.text
            time.replace(" . Updated ago", "")
            link_segment = link_element["href"]
            if link_segment not in flag_set:
                ret_map[link_segment[:-1] + ".html"] = {"title" : title, "sub" : " - Reuters" + " (" + time + ")"}

    return ret_map

    # print(li_elements)

def page_former(map, news_source, section) -> dict:

    section_pages = section + '_pages'
    file_dir = 'C:/Users/ahadb/Desktop/Simpl News/pages/' + section_pages + '/'

    new_map = {}

    for key in map:
        # temp = key
        # temp = temp.replace("https://www.reuters.com", "") #TODO: Generalize
        # file_name = temp[:-1] + ".html"
        # file_name = file_name[7:] #TODO: Change this to something generalizable
        # print(key)
        # file_name = key[7:]
        # filepath = os.path.join(file_dir, file_name)
        filepath = os.path.join(file_dir, key)

        
        # This try-except block should solve the re-opening pages issue 
        # try:
            # f = open(file_name, "x")
        f = open(filepath, "x")

        # except:
        #     print("Fucked")
        #     continue
        # else:
        link = requests.get("https://www." + news_source + ".com" + key)
        link_soup = bs4.BeautifulSoup(link.text, "lxml")
        if news_source == "reuters":
            paragraphs = link_soup.find_all('p', class_='text__text__1FZLe text__dark-grey__3Ml43 text__regular__2N1Xr text__large__nEccO body__full_width__ekUdw body__large_body__FV5_X article-body__element__2p5pI')
        else:
            paragraphs = link_soup.find_all('p')
        new_string = ""
        for element in paragraphs:
            element_text = element.text
            temp = "<p>" + element_text + "</p>"
            new_string += temp
        to_write = "<!DOCTYPE html><head><h1>Simpl News</h1></head><body>" + new_string + "</body></html>"
        print(to_write)

        f.write(to_write)

        f.close()

        # shutil.move(key, section_pages + key)
        shutil.move(filepath, os.path.join(file_dir, section_pages, key))  #

        new_map[section_pages + key] = map[key]

        # f = open(filepath, "x")


        # link = requests.get(key)
        # link_soup = bs4.BeautifulSoup(link.text, "lxml")
        # paragraphs = link_soup.find_all('p')
        # new_map["world"] = paragraphs
        

    # return new_map
    return new_map
        

# world_link_list = []

# print(section_map)
def reuters_parser_initial_function(section_map) -> dict:
    for title, link in section_map.items():
        if title == "/world/":
            world_request = requests.get(link)
            world_soup = bs4.BeautifulSoup(world_request.text, "lxml")
            world_map = reuters_parser(world_soup)
            return page_former(world_map, "reuters", "world")
        elif title == "/business/":
            business_request = requests.get(link)
            business_soup = bs4.BeautifulSoup(business_request.text, "lxml")
            business_map = reuters_parser(world_soup)
        elif title == "/technology/":
            tech_request = requests.get(link)
            tech_soup = bs4.BeautifulSoup(tech_request.text, "lxml")
            technology_map = reuters_parser(world_soup)

@app.route("/")
# def index():
#     world_url = url_for('')
#     return flask.render_template('index.html', )

@app.route('/world.html')
def world():
    page_urls = reuters_parser_initial_function(section_map)
    return flask.render_template('world.html', page_urls = page_urls)

if __name__ == '__main__':
    app.run(debug=True)



    

        
    

