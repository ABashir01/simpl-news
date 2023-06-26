#TODO: Consider finding a way to remove world/europe, world/india, etc. from titles


import bs4
import requests
import flask
import os
import shutil

app = flask.Flask(__name__)

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
                link_segment = link_segment[1:-1]
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
            time = time.replace(" . Updated ago", "")
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
    
def reuters_page_former(map):


    for key in map:
        # temp = key.replace('/', '___')
        # temp = temp[3:]
        temp = key.split('/')[-1]
        filepath = "pages/world_pages/" + temp + ".html"
        print(filepath)
        
        # try:
        #     f = open(filepath, 'x')
        # except:
        #     continue
        
        link = requests.get("https://www.reuters.com" + key)
        link_soup = bs4.BeautifulSoup(link.text, "lxml")
        paragraphs = link_soup.find_all('p', class_='text__text__1FZLe text__dark-grey__3Ml43 text__regular__2N1Xr text__large__nEccO body__full_width__ekUdw body__large_body__FV5_X article-body__element__2p5pI')
        
        new_string = ""
        for element in paragraphs:
            element_text = element.text
            temp = "<p>" + element_text + "</p>"
            new_string += temp
        to_write = "<!DOCTYPE html><head><h1>Simpl News</h1></head><body>" + new_string + "</body></html>"
        
        # f.write(to_write)
        # f.close()
        



new_map = reuters_main_page_parser()
sec_map = reuters_section_parser(new_map)
reuters_page_former(sec_map["world"])
