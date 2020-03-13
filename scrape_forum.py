#!/usr/bin/env python

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import sys
import re
from datetime import date

def main():
    url = sys.argv[1]
    out_file_name = url.split('/')[-2].split('.')[0] + "-" + str(date.today()) + ".txt"
    thread_posts = []
        
    thread_posts = recursive_crawler(url, thread_posts)
    print("Scraped " + str(len(thread_posts)) + " forum posts")

    #parse list of entries and output to file
    with open(out_file_name, 'w') as fo:
        for entry in thread_posts:
            for k,v in entry.items():
                print(': '.join([k, v]), file = fo)
            print('\n', file = fo)
    

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def get_next_page(url):
    url_base = url.split("/index")[0]
    
    req = get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    
    next_page_url=""
    for a in soup.select('a'):
        if a.text=="Next":
            next_page_url = url_base + a['href']
    if next_page_url!="":
        return(next_page_url)
    else:
        return("LAST_PAGE")

def get_page_posts(url):
    
    post_keys=["User", "Date","Index", "Text"]
    page_db=[]
    raw_html=simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')
    
    for article in html.select('article'):
        post_dict= dict.fromkeys(post_keys)
        for div in article.select('div'):
            if 'class' in div.attrs:
                #Get Username
                if div['class']==['message-userDetails']:
                    username = div.select('h4')[0].text
                    post_dict["User"]=username
                
                #Get post date
                if div['class']==['message-attribution-main']:
                    post_date = div.select('a')[0].text
                    post_dict["Date"]=post_date.strip()

                #Get post index
                if div['class']==['message-main', 'js-quickEditTarget']:
                    for ul in div.select('ul'):
                        a=ul.select('a')
                        if len(a)!=0:
                            post_index=a[-1].text.strip()[1:]
                            post_dict["Index"]=post_index

                #Get post text
                if div['class']==['bbWrapper']:
                    post_text_list=re.sub(r"[\n\t]+", "\n", div.text).strip().split("\n")
                    post_text = '\n'.join(post_text_list)
                    post_dict["Text"]=post_text
            

        if post_dict["User"]!=None:
            page_db.append(post_dict)

    return(page_db)

def recursive_crawler(url, db):
    page_posts = get_page_posts(url)
    next_page_url = get_next_page(url)
    db = db + page_posts
    
    if next_page_url=="LAST_PAGE":
        return(db)
    else:
        return(recursive_crawler(next_page_url, db))


if __name__ == "__main__":
    main()

