from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route("/")
def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

@app.route("/scrape")
def scrape():
    # collect the latest News Title and Paragraph Text. Assign the text to variables that you can reference later.
    browser = init_browser()
    mars_data = {}
    mars_url = 'https://mars.nasa.gov/news/'
    browser.visit(mars_url)
    newshtml = browser.html
    newsoup = bs(newshtml, 'html.parser')
    time.sleep(3)
    news_title = newsoup.find('div', class_='content_title').text.strip()
    news_p = newsoup.find('div', class_='article_teaser_body').text.strip()
    mars_data['news_title'] = news_title
    mars_data['news_parag'] = news_p

    # find the image url for the current Featured Mars Image and assign the url string to a variable
    jpl_url_search = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    jpl_url = 'https://www.jpl.nasa.gov'
    browser.visit(jpl_url_search)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(1)
    jplhtml = browser.html
    jplsoup = bs(jplhtml, 'html.parser')
    img_path = jplsoup.find('img', class_='fancybox-image')['src']
    featured_image_url = jpl_url + img_path
    mars_data['featured_image_url'] = featured_image_url

    # scrape the latest Mars weather tweet
    # twitter log in window pops up during initial run, should work second time running
    marsweatherurl = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(marsweatherurl)
    time.sleep(1)
    mars_html = browser.html
    mars_soup = bs(mars_html, 'html.parser')
    mars_weather = mars_soup.find('p', class_='TweetTextSize')
    mars_data['mars_weather'] = mars_weather.text.strip().replace('hPapic', 'hPa pic')

    # use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc
    mars_facts_url = 'https://space-facts.com/mars/'
    browser.visit(mars_facts_url)
    table = pd.read_html(mars_facts_url)
    df = table[0]
    df.columns = ['description', 'value']
    df = df.set_index('description')
    mars_facts = df.to_html(index=True, header=True)
    mars_data['table'] = mars_facts


    # obtain high resolution images for each of Mar's hemispheres
    hemisph_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hlist = ['Cerberus Hemisphere', 'Schiaparelli Hemisphere', 'Syrtis Major Hemisphere', 'Valles Marineris Hemisphere']
    hemisph_img_urls = []
    for h in hlist:
        img_dict = {}
        browser.visit(hemisph_url)
        browser.click_link_by_partial_text(h)
        time.sleep(1)
        browser.find_link_by_text('Sample').first.click()
        
        browser.windows.current = browser.windows[-1]
        hemisph_soup = bs(browser.html, 'html.parser')
        img_url = hemisph_soup.find('img')['src']
        img_dict = {'title': h, 'img_url': img_url}
        hemisph_img_urls.append(img_dict)   
        browser.windows[-1].close()
        time.sleep(1)
    mars_data['hemisph_img'] = hemisph_img_urls
    browser.quit()

    return mars_data