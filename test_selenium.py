from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

import MySQLdb
from datetime import datetime
from decimal import Decimal

# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

options = Options()
options.use_chromium=True
#options.add_argument("headless")
service = Service(verbose = False)

url='https://finance.yahoo.com/quote/UNTR.JK/financials?p=UNTR.JK'
                # txt_ticker = 'UNTR'
          
debug=True                
driver = webdriver.Edge(service = service, options = options)
driver.get(url)
#link_stock_header = driver.find_element(By.XPATH,'//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1') not working
#link_stock_header = driver.find_element(By.XPATH,'//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[1]/div/div/section/h1') #working
link_stock_header = driver.find_element(By.XPATH,'/html/body/div[2]/main/section/section/section/article/section[1]/div[1]/div/div/section/h1') # also working
if link_stock_header is not None:
  if debug == True :
     print("Stock Name :", link_stock_header.text)
    
#//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[1]/div/div/section/h1 // copy path
#/html/body/div[2]/main/section/section/section/article/section[1]/div[1]/div/div/section/h1 // copy full path