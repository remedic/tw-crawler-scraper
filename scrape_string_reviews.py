#!/usr/bin/env python

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def main():
    run='all'
    url = 'https://www.tennis-warehouse.com/stringcontent.html'
    base_url = 'https://www.tennis-warehouse.com'

    variables = ['Name', 'Price', 'Overall', 'Power', 'Spin', 'Comfort', 'Control', 'Touch/Feel', 'String Movement', 'Playability Duration', 'Durability', 'URL'] 

    if run=='test':
        #url = "https://www.tennis-warehouse.com/reviews/BRPMB15/BRPMB15review.html"
        #url = "https://www.tennis-warehouse.com/reviews/WRS17/WRS17review.html"
        url = "https://www.tennis-warehouse.com/reviews/VCYC/VCYCreview.html"
        review = get_vars(base_url, url, variables)
        print(review) 


    if run=='all':
        db = {}
        index = 1
        req = get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        brand_links = soup.find_all('ul', {'class':'lnav_section'})
        for bl in brand_links:
            for link in bl.select('li'):
                if 'String' in link.text.strip().split()[-1]:
                    url2 = base_url + link.find('a')['href']
                    brand = get(url2)
                    soup_brand = BeautifulSoup(brand.text, "html.parser")
                    review_links = soup_brand.find_all("a",{'class':'review'})
                    while index < 10:
                        for rl in review_links:
                            url3 = base_url + rl['href']
                            print(url3)
                            try:
                                review = get_vars(base_url, url3, variables)
                                db[index] = review
                                index = index + 1
                            except:
                                pass
        
        db = remove_dups(db)

        with open("strings.tsv", "w") as f:
            print('\t'.join(variables), file = f)
            for k,v in db.items():
                vals=list(db[k].values())
                vals = ['None' if v is None else v for v in vals]
                print('\t'.join(vals), file = f)

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


def is_good_response(resp):
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


def get_vars(base_url, url, review_vars):
    """
    Pull review variabes from review webpage table.
    """
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')
    
    review = dict.fromkeys(review_vars)
  
    #NAME
    review['Name'] = html.find('h1').text.replace(' String Review', '')

    #PRICE
    if html.find('div', {'id':'pricebox'}):
        review['Price'] = html.find('div', {'id':'pricebox'}).find('h1').text
    if html.find('span', {'class':'price'}):
        review['Price'] = html.find('span', {'class':'price'}).text.replace('Price: ', '')
    
    #REVIEW VARIABLES
    if html.find('div', {'class':'score_box'}):
        for tr in html.find('div', {'class':'score_box'}).select('tr'):
            fields = tr.text.strip().split('\n')
            if fields[0] in review_vars:
                review[fields[0]] = fields[1]
            if fields[0] in ['Touch','Feel']:
                review['Touch/Feel'] = fields[1]
    if html.find('div', {'class':'review_scores'}):
        for tr in html.find('div', {'class':'review_scores'}).select('tr'):
            fields = tr.text.strip().split('\n')
            if fields[0] in review_vars:
                review[fields[0]] = fields[1]
            if fields[0] in ['Touch','Feel']:
                review['Touch/Feel'] = fields[1]

    #URL
    if html.find('div', {'id':'pricebox'}):
        review['URL'] = base_url + html.find('div', {'id':'pricebox'}).find('a')['href']
    if html.find('div', {'class':'review_btns'}):
        review['URL'] = html.find('a', {'class':'button'})['href']

    return(review)

def remove_dups(db):
    """
    Remove duplicate review rows (excluding url and price)
    """
    
    for k,v in db.items():
        for x,y in v.items():
            print(x)

    return(db)

if __name__ == "__main__":
    main()
