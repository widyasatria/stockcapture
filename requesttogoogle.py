# Import required modules
from lxml import html
import requests
 
# Request the page
page = requests.get('https://www.google.com/finance/quote/PTBA:IDX')
 
# Parsing the page
# (We need to use page.content rather than
# page.text because html.fromstring implicitly
# expects bytes as input.)
print(page.content)
tree = html.fromstring(page.content) 


# Get element using XPath
buyers = tree.xpath('//*[@id="__next"]/div[2]/div[2]/div[1]/div[1]/div[3]/div/div[1]/div[1]')
print(buyers)