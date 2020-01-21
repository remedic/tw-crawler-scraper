#!/usr/bin/env python

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def main():
    run='test'
    url ='https://www.tennis-warehouse.com'

    variables = ['Name','Overall', 'Groundstrokes', 'Volleys', 'Serves', 'Returns', 'Power', 'Control', 'Maneuverability', 'Stability', 'Comfort', 'Touch/Feel', 'Topspin', 'Slice', 'Length', 'Head Size', 'Weight', 'Balance Point', 'Construction', 'Composition', 'String Pattern', 'Flex Rating', 'Swing Weight', 'URL']

    if run=='test':
        url ='https://www.tennis-warehouse.com/reviews/EZ1HB/EZ1HBreview.html'
        #url = 'https://www.tennis-warehouse.com/reviews/PRF97A/PRF97Areview.html'
        #url = 'https://www.tennis-warehouse.com/reviews/BPD1H/BPD1Hreview.html'
        #url = 'https://www.tennis-warehouse.com/Reviews/BPAR/BPARReview.html'
        #url = 'https://www.tennis-warehouse.com/reviews/HG3RMP/HG3RMPreview.html'
        review = get_vars(url, variables)
        print(review)

    if run=='all':
        db = {}
        index = 1
        req = get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        racquet_brand_links = soup.find_all("a")
        for rbl in racquet_brand_links:
            if 'racquets' in rbl['href']:
                url2 = url + rbl['href']
                req_brand = get(url2)
                soup_brand = BeautifulSoup(req_brand.text, "html.parser")
                review_links = soup_brand.find_all("a",{'class':'review'})
                for rl in review_links:
                    url3 = url + rl['href']
                    print(url3)
                    try:
                        review = get_vars(url3, variables)
                        db[index] = review
                        index = index + 1
                    except:
                        pass
        with open("racquets.tsv", "w") as f:
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


def get_vars(url, review_vars):
    """
    Pull review variabes from review webpage table.
    """
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')
    
    review = dict.fromkeys(review_vars)
    
    for h1 in html.select('h1'):
        review['Name']=h1.text.replace(' Racquet Review', '')

    for div in html.select('div'):
        if 'class' in div.attrs:
            if div['class']==['overall', 'fr']:
                fields=div.text.strip().split('\n')
                review[fields[0]]=fields[1]
            if div['class']==['review_btns']:  
                for a in div.select('a'):
                    if a.text=='Order Now':
                        review['URL']=a['href']
            if div['class']==['review_scores'] or div['class']==['racquet_specs', 'cf']:
                for tr in div.select('tr'):
                    td_list = []
                    for th in tr.select('th'):
                        td_list.append(th.get_text())
                    for td in tr.select('td'):
                        td_list.append(td.text)
                    if len(td_list)>0:
                        if td_list[0] in review_vars:
                            if td_list[0]=="Balance Point":
                                review[td_list[0]]=td_list[2]
                            else:
                                review[td_list[0]]=td_list[1]
            if div['class']==['scores']:
                print(div)
                for tr in div.select('tr'):
                    td_list=[]
                    for th in tr.select('th'):
                        td_list.append(th.get_text())
                    for td in tr.select('td'):
                        td_list.append(td.get_text())
                    if td_list[0]=="Balance Point":
                        review[td_list[0]]=td_list[2]
                    else:
                        review[td_list[0]]=td_list[1]

    
    return(review)

if __name__ == "__main__":
    main()
