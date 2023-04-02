# Parsing Amazon using Selenium and BeautifulSoup4 #

<br>

## Description ##

The parser can parse products from the Amazon online store according to your request. The Request can be a link to an Amazon page (a selection of products or a category of products) or a search query.
<br>

With the help of the parser you can get the following product information: 
1. Title
2. About_item
3. Full_price
4. Purchase_price
5. Rating
6. Reviews
7. Characteristics
8. Product URL

By default, information is recorded in the csv file format.

<br>

## Quick Start ##

1. Download the git repository on your computer
2. Download all requirements from <b> requirements.txt </b>
3. Download <a href="https://chromedriver.chromium.org/downloads">chromedriver</a> in project directory and Google Chrome for your OS (Chromedriver must be compatible with your version of Chrome)
4. Turn on/off headless mode
5. Run script <b> main.py </b>
6. Enjoy!)

<br>

## Install requirements ##

To install all requirements you must open terminal and in project directory input next command
    
    pip3 install -r requirements.txt

For Windows:
    
    pip install -r requirements.txt

<br>

## Turn on/off headless mode ##

In 18 string you can configurate headless mode

    headless_mode = True

If you want to deactivate headless mode choose value False

    headless_mode = False