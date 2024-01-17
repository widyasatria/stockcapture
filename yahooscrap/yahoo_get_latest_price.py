#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

import os
from selenium import webdriver
#pip install msedge-selenium-tools
import datetime

import MySQLdb
from pathlib import Path
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from configparser import ConfigParser

def upd_stock_last_modify(conn,txt_ticker):
    cursor = conn.cursor()
    qry="update stocks set stock_intraday = now() where ticker= %s "
    cursor.execute(qry,(txt_ticker,))
    conn.commit()

def insert_stock_price(vals,conn):
    # insert to database'
    cmd = 'insert into stock_intraday(ticker, url, last_price, price_change, txt_last_update_in_site,inter_val,updated_at)'
    cmd = cmd + 'values ( %s, %s, %s, %s, %s, 15, now() ) '
    val= (vals[0],vals[1],vals[2],vals[3],vals[4])
    print((vals[0],vals[1],vals[2],vals[3],vals[4]))
    
    cursor = conn.cursor()
    
    #cursor.execute(cmd,(str(vals[0]),str(vals[1]),str(vals[2]),str(vals[3]),str(vals[4])) )
    cursor.execute(cmd,val)
    result = conn.commit()
    
    return result

def main():
    
    #requirement selenium versi 4.13.0
    #ms edge webdriver : https://msedgedriver.azureedge.net/119.0.2151.72/edgedriver_win64.zip
    # mysql-connector-python
    
    # parameter executable_path ini sudah tidak di bisa di pakai di selenium versi 4, caranya ketik di command prompt echo %Path% untuk mengetahui existing environment variable
    # kemudian copy msedge webdriver ke salah satu path yang terdaftar.
    
    # driver = webdriver.Edge(executable_path=r'C:\Users\wardians\stockcapture\msedgedriver.exe')
    # references : https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/ie-mode?tabs=python
    
    options = Options()
    options.use_chromium=True
    options.add_argument("headless")
    options.add_argument("log-level=2")
    service = Service(verbose = False)
    debug = True
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    config_path = os.path.join(up_onefolder,"conf")
    conf_file = os.path.join(config_path,"config.ini")
    
    config = ConfigParser()
    config.read(conf_file)

    conn = MySQLdb.connect(
    host=config.get('db_connection', 'host'),
    user=config.get('db_connection', 'user'),
    password=config.get('db_connection', 'pwd'),
    database=config.get('db_connection', 'db'),
    auth_plugin=config.get('db_connection', 'auth')
    )
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ticker FROM stocks order by stock_intraday")
        result = cursor.fetchall()  
        driver = webdriver.Edge(service = service, options = options)
        if result is not None:      
            for x in result:
                txt_ticker = x[0]
                print('=== Populating Intraday Price for '+ txt_ticker)
                
                if debug == True :
                    print(' Getting price from : https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK')

                
                url='https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK'
               
                driver.get(url)
              
                
                driver.implicitly_wait(4)

                link_stock_header = driver.find_element(By.XPATH,'//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1')
                if link_stock_header is not None:
                    if debug == True :
                        print("Stock Name :", link_stock_header.text)
                    
                txt_income_statement = driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/h3/span')
                if debug == True :
                    print("txt_income : ", txt_income_statement.text)
                
                txt_price=driver.find_element(By.XPATH,'//*[@id="quote-header-info"]/div[3]/div[1]/div')
                
                txt_prices= txt_price.text.split("\n")
                if debug == True :    
                    print("pandjang text ", len(txt_prices))
                txtpricenchange = txt_prices[0].split(" ")
            
                txt_price = txtpricenchange[0].split(".")
                if debug == True :
                    print("txt price  : ", txt_price[0].replace(",",""))
                
                txt_price_change=txtpricenchange[1].replace("(","").replace(")","")
                if debug == True :
                    print("txt price Change : ", txt_price_change)
                    print("txt price line 2 : ", txt_prices[1])
                
                values=[]
                values.append(x[0])
                values.append(url)
                values.append(Decimal(txt_price[0].replace(",",""))) #last_price
                values.append(txt_price_change) #price_change
                values.append(txt_prices[1])
                values.append(datetime.datetime.now())
                res = insert_stock_price(values,conn)
                
                upd_stock_last_modify(conn,txt_ticker)
                if debug == True :
                    print("exec result ",res)
                
    except MySQLdb.Error as ex:
        try:
            print  (f"MySQL Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            return None
        except IndexError:
            print (f"MySQL Error: %s",str(ex))
            return None
    except MySQLdb.OperationalError as ex:
        print(ex)
        return None
    except TypeError as ex:
        print(ex)
        return None
    except ValueError as ex:
        print(ex)
        return None
    except Exception as ex:
        print('Generic Error caught on: '+ txt_ticker +' : ' + str(ex) )
        return None
    finally:
        conn.close
              

if __name__ == "__main__":
    main()