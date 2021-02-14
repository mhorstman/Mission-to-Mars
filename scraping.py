#!/usr/bin/env python

# Import Splinter, BeautifulSoup and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
   # Initiate headless driver for deployment
    browser = Browser('chrome', executable_path="chromedriver", headless=True)

    # Run all scraping functions and store results in dictionary
    news_title, news_paragraph = mars_news(browser)
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere_image_urls": hemisphere_image(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# ### NASA Featured Articles
# Define function to scrape Mars news 
def mars_news(browser):
    # Scrape Mars News
    # # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Parse the HTML code into a variable and then finds <ul class="item_list"> and then <li class="slide"> 
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_='article_teaser_body').get_text()
        print("mars_news function complete")
    except AttributeError:
        return None, None
    
    return news_title, news_p


# ### JPL Space Images Featured Images
# Define function to scrape images
def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        print("featured_image function complete")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

# ### Mars Facts Table
# Define function to scrape Mars facts table
def mars_facts():
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
        print("mars_facts function complete")
    except BaseException:
        return None

    df.columns=['description', 'Mars']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-stripped")

# ### Get Mars Hemisphere Info
def hemisphere_image(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    html_soup = soup(html, 'html.parser')
    hemi_elements = html_soup.find_all('div', class_='description')

    for element in hemi_elements:
        # Create an empty dictionary
        hemisphere = {}
        
        # Navigate to the full-resolution image
        image_ref_link = element.find('a', class_='itemLink product-item')
        image_link = f"https://astrogeology.usgs.gov{image_ref_link.get('href')}"
        browser.visit(image_link) 
        
        # Retrieve the full-resolution image url and title
        full_image_url = browser.links.find_by_text('Sample')['href']
        title = browser.find_by_tag('h2').text
        
        # Add the url and title to the dictionary
        hemisphere = {'img_url': full_image_url, 'title' : title}
        hemisphere_image_urls.append(hemisphere)

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())