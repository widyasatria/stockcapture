#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

import os, time, logging
from selenium import webdriver
#pip install msedge-selenium-tools
#import datetime
from datetime import datetime, timedelta
import mysql.connector
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
    # insert to databaseszadasa '
    cmd = 'insert into stock_intraday(ticker, url, last_price, price_change,price_percent_change, txt_last_update_in_site, inter_val,updated_at)'
    cmd = cmd + 'values ( %s, %s, %s, %s, %s,%s, 15, now() ) '
    val= (vals[0],vals[1],vals[2],vals[3],vals[4],vals[5])
    print((vals[0],vals[1],vals[2],vals[3],vals[4],vals[5]))

    cursor = conn.cursor()
    
    #cursor.execute(cmd,(str(vals[0]),str(vals[1]),str(vals[2]),str(vals[3]),str(vals[4])) )
    cursor.execute(cmd,val)
    result = conn.commit()
    
    return result

def rotate_log_file(log_name,log_file_path,log_file_name):
    curr_date = datetime.now()
    log_file_prev_date = curr_date - timedelta(days = 1)
    #print('prevdate :',log_file_prev_date.strftime("%d-%m-%Y"))
    fname_prev_log_file= log_name+log_file_prev_date.strftime("_%d-%m-%Y")+".log"
    prev_log_file= os.path.join(log_file_path,fname_prev_log_file)
    #print(prev_log_file)
  
    if not os.path.exists(prev_log_file) and os.path.exists(log_file_name) :
        os.rename(log_file_name,prev_log_file)

def main():
    
    #requirement selenium versi 4.13.0
    #ms edge webdriver : https://msedgedriver.azureedge.net/119.0.2151.72/edgedriver_win64.zip
    # mysql-connector-python
    
    # parameter executable_path ini sudah tidak di bisa di pakai di selenium versi 4, caranya ketik di command prompt echo %Path% untuk mengetahui existing environment variable
    # kemudian copy msedge webdriver ke salah satu path yang terdaftar.
    
    # driver = webdriver.Edge(executable_path=r'C:\Users\wardians\stockcapture\msedgedriver.exe')
    # references : https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/ie-mode?tabs=python
    
    start_time = datetime.now()
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
      
  
    log_path = os.path.join(up_onefolder,"log")
    log_file = os.path.join(log_path,"yahoo_get_latest_price.log")
    
    rotate_log_file("yahoo_get_latest_price",log_path,log_file)
    
    #DEBUG
    #INFO
    #WARNING
    #ERROR
    #CRITICAL
    my_log_format= '%(asctime)s : %(name)s : %(levelname)s : %(message)s - Line : %(lineno)d'
    logging.basicConfig(filename=log_file,level=logging.INFO, format=my_log_format, datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger('yahoo_get_latest_price')
    logger.info('=================START SCRIPT yahoo_get_latest_price ================= ')
    
    options = Options()
    options.use_chromium=True
    #options.add_argument("headless")
    options.add_argument("log-level=2")
    service = Service(verbose = True)
    debug = True
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    config_path = os.path.join(up_onefolder,"conf")
    conf_file = os.path.join(config_path,"config.ini")
    
    config = ConfigParser()
    config.read(conf_file)

    conn = mysql.connector.connect(
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
                try:
                    txt_ticker = x[0]
                    print('=== Populating Intraday Price for '+ txt_ticker)
                    
                    if debug == True :
                        print(' Getting price from : https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK')

                    
                    url='https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK'
                
                    driver.get(url)
                
                    
                    driver.implicitly_wait(4)

                    link_stock_header = driver.find_element(By.XPATH,'//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[1]/div/div/section/h1')
                    if link_stock_header is not None:
                        if debug == True :
                            print("Stock Name :", link_stock_header.text)
                        
                    # txt_income_statement = driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/h3/span')
                    # if debug == True :
                    #     print("txt_income : ", txt_income_statement.text)
                
                    
                    txt_price=driver.find_element(By.XPATH,'//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section/div[1]/div[1]/span')
                    
                    print("txt price ", txt_price.text)
                    
                    txt_price_change = driver.find_element(By.XPATH,'//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section/div[1]/div[2]/span')
                    print("txt price change ", txt_price_change.text)
                    
                    txt_percentage_price_change = driver.find_element(By.XPATH,'//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section/div[1]/div[3]/span')
                    print("txt percentage price change ", txt_percentage_price_change.text)
                    
                    txt_last_updated_in_site = driver.find_element(By.XPATH,'//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section/div[2]/span/span')
                    print("txt last updated in site ", txt_last_updated_in_site.text)
                    
             
                #time.sleep(30)
     
                
                    values=[]
                    values.append(x[0])
                    values.append(url)
                    values.append(Decimal(txt_price.text.replace(",",""))) #last_price
                    values.append(txt_price_change.text) #price_change
                    values.append(txt_percentage_price_change.text)
                    values.append(txt_last_updated_in_site.text)
                    #values.append(datetime.datetime.now())
                    res = insert_stock_price(values,conn)
                    
                    upd_stock_last_modify(conn,txt_ticker)
                    if debug == True :
                        print("exec result ",res)
                
                except NoSuchElementException as ex:   
                    print('Error on getting ' + txt_ticker + ' data caught on: ' + url +' '+  str(ex) ) 
                    logger.error('Error on getting ' + txt_ticker + ' data caught on: ' + url +' '+  str(ex) ) 
                    pass

    except mysql.connector.Error as ex:
        print  (f"MySQL Error [%d]: %s %s",(ex.args[0], ex.args[1]))
        return None
    except mysql.IndexError as ex:
        print (f"MySQL Error: %s",str(ex))
        return None
    except mysql.ValueError as ex:
        print(ex)
        return None
    except IndexError as ex:
        print (f"MySQL Index Error: %s",str(ex))
        return None
    except Exception as ex:
        print('Generic Error caught on: '+ txt_ticker +' : ' + str(ex) )
        return None
    
    finally:
        conn.close
              

if __name__ == "__main__":
    main()