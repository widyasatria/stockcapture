
# Import required modules
from lxml import html
import requests
 
# Request the page
page = requests.get('https://webscraper.io/test-sites/e-commerce/allinone')
 
# Parsing the page
tree = html.fromstring(page.content)
 
# Get element using XPath
prices = tree.xpath(
    '//div[@class="col-sm-4 col-lg-4 col-md-4"]/div/div[1]/h4[1]/text()')
print(prices)