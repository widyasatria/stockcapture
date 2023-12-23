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
options.add_argument("headless")
service = Service(verbose = False)

url='https://finance.yahoo.com/quote/UNTR.JK/financials?p=UNTR.JK'
                # txt_ticker = 'UNTR'
          
                
driver = webdriver.Edge(service = service, options = options)
driver.get(url)
    
    
