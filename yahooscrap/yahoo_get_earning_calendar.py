#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

# FILE INI SUDAH TIDAK BISA DI RUN LANGSUNG HARUS DIPANGGIL OLEH ../stockplus_scheduler.py

import os, time
from selenium import webdriver


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from pathlib import Path

import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal

# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from configparser import ConfigParser
import logging

debug = True

def rotate_log_file(log_name,log_file_path,log_file_name):
    curr_date = datetime.now()
    log_file_prev_date = curr_date - timedelta(days = 1)
    #print('prevdate :',log_file_prev_date.strftime("%d-%m-%Y"))
    fname_prev_log_file= log_name+log_file_prev_date.strftime("_%d-%m-%Y")+".log"
    prev_log_file= os.path.join(log_file_path,fname_prev_log_file)
    #print(prev_log_file)
  
    if not os.path.exists(prev_log_file) and os.path.exists(log_file_name) :
        os.rename(log_file_name,prev_log_file)

def populate_earnings_calendar(conn, txt_ticker, txt_earning_date, txt_eps_estimate, txt_reported_eps, txt_surprise_eps):
    cursor = conn.cursor()
    if debug==True:
        print("Original Date from web : " + txt_earning_date)
 
    x_date = txt_earning_date.split("WIB")
    date_from_web = x_date[0]
    
    #insert hanya jika tidak ada record
    qryselect="select count(*) from stock_earnings_calendar where ticker='"+txt_ticker+"' and earnings_date = '" + date_from_web + "'"
    cursor.execute(qryselect)
    result = cursor.fetchone()
      
    if result is not None:
       cnt_record = result[0]    
       if int(cnt_record) == 0:
           qryinsert=" insert into stock_earnings_calendar(ticker, earnings_date, eps_estimate, reported_eps, surprise_eps, created_at, updated_at) "
           qryinsert += " values('"+ txt_ticker + "','" + date_from_web +"','" + txt_eps_estimate +"','" + txt_reported_eps +"','" + txt_surprise_eps +"', now(), now()) "
       
           cursor.execute(qryinsert)
           conn.commit()
   

def upd_stock_last_modify(conn,txt_ticker):
    cursor = conn.cursor()
    qry="update stocks set stock_earning_calendar = now() where ticker= %s "
    cursor.execute(qry,(txt_ticker,))
    conn.commit()
    
    

def main():
    #requirement selenium versi 4.13.0
    #ms edge webdriver : https://msedgedriver.azureedge.net/119.0.2151.72/edgedriver_win64.zip
    
    # parameter executable_path ini sudah tidak di bisa di pakai di selenium versi 4, caranya ketik di command prompt echo %Path% untuk mengetahui existing environment variable
    # kemudian copy msedge webdriver ke salah satu path yang terdaftar.
    
    # driver = webdriver.Edge(executable_path=r'C:\Users\wardians\stockcapture\msedgedriver.exe')
    # references : https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/ie-mode?tabs=python
    
    start_time = datetime.now()
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
      
  
    log_path = os.path.join(up_onefolder,"log")
    log_file = os.path.join(log_path,"yahoo_get_earning_calendar.log")
    
    rotate_log_file("yahoo_get_earning_calendar",log_path,log_file)
    
    
    #DEBUG
    #INFO
    #WARNING
    #ERROR
    #CRITICAL
    my_log_format= '%(asctime)s : %(name)s : %(levelname)s : %(message)s - Line : %(lineno)d'
    logging.basicConfig(filename=log_file,level=logging.INFO, format=my_log_format, datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger('yahoo_get_earning_calendar')
    logger.info('=================START SCRIPT yahoo_get_earning_calendar================= ')
    
    options = Options()
    options.use_chromium=True
    options.add_argument("headless")
    options.add_argument("log-level=2")
    service = Service(verbose = False)
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
    
        cursor.execute("SELECT ticker FROM stocks order by stock_earning_calendar")
        result = cursor.fetchall()  
        driver = webdriver.Edge(service = service, options = options)
        if result is not None:      
            for x in result:
                txt_ticker = x[0]
                print('=== Populating Stock Earning Calendar for '+ txt_ticker)
                logger.info('=== Populating Stock Earning Calendar for for '+ txt_ticker)
                
                url='https://finance.yahoo.com/calendar/earnings/?symbol='+x[0]+'.JK'
                
               
                stime = datetime.now()
          
                driver.get(url)

                time.sleep(1)
               
                driver.implicitly_wait(4)
                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                # to get the headers
                       
                txt_table_xpath = '//*[@id="nimbus-app"]/section/section/section/article/main/main/main/div/table/tbody'
                try:
                    table_earnings = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, txt_table_xpath))) 

                
                    if table_earnings is not None:
                        print("table ketemu")
                        time.sleep(0.5)
                        driver.implicitly_wait(4)
                        tbl_earnings = driver.find_elements(By.XPATH,txt_table_xpath)
                        
                        for tr_data in tbl_earnings:
                            tr_earnings = tr_data.find_elements(By.TAG_NAME,"tr")
                            if debug==True:
                                print("jumlah row " + str(len(tr_earnings)))
                            for txt_tr in tr_earnings:
                                #print("ini tr :" + txt_tr.text)
                                td_earnings = txt_tr.find_elements(By.TAG_NAME,"td")
                                # print(td_earnings[0].text)
                                # print(td_earnings[2].text) # Earnings_date
                                # print(td_earnings[3].text) # eps estimate
                                # print(td_earnings[4].text) # reported eps
                                # print(td_earnings[5].text) # surprise
                                populate_earnings_calendar(conn,txt_ticker,td_earnings[2].text, td_earnings[3].text,td_earnings[4].text,td_earnings[5].text)
                            
                           
                except Exception as ex:
                    print('Error on getting ' + txt_ticker + ' data caught on: ' + str(ex) ) 
                    logger.error('Error on getting ' + txt_ticker + ' data caught on: ' + str(ex) )  
                      
                    pass
                
                upd_stock_last_modify(conn,txt_ticker)               
                etime = datetime.now()
                print('Duration for this url {}'.format(etime - stime))        
                     
        
        end_time = datetime.now()
        if debug==True:
            print('Duration: {}'.format(end_time - start_time))    
        
        logger.info('Duration: {}'.format(end_time - start_time))    
        logger.info('=================End script Stock Earning Calendar ================= ')
        
    except mysql.connector.Error as ex:
        print('Mysql Generic Error caught on: ' + str(ex))
        logger.error('Mysql Generic error caught on: ' + str(ex))
        try:
            print(f"MySQL Generic Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            logger.error(f"MySQL Generic Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            return None
        except IndexError:
            print (f"MySQL Index Error: %s",str(ex))
            logger.error(f"MySQL Index Error: %s",str(ex))
            return None
    except TypeError as ex:
        print(ex)
        logger.error(ex)
        return None
    except ValueError as ex:
        print(ex)
        logger.error(ex)
        return None
    except Exception as ex:
        print('Generic Error caught on: ' + str(ex) )
        logger.error('Generic Error caught on: ' + str(ex) )
        return None
    finally:
        conn.close
        driver.quit()
        

if __name__ == "__main__":
    main()

