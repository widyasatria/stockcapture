
import os, time
from selenium import webdriver
#pip install msedge-selenium-tools
from pathlib import Path
import os
from configparser import ConfigParser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

import mysql.connector
from datetime import datetime, timedelta
from dateutil import parser
from decimal import Decimal
import csv
# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
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

def isnull(val):
    if val is None or val == 'null':
        val = Decimal(0)
    return val

def cleansing_data(val):
    if (val.find(",")>-1 or val.find(".")>-1) and val.find("k")==-1 :
        txt_value = str(val.replace(",","").strip())
    return txt_value

def update_daily_stock_price():
    start_time = datetime.now()
    
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
    logger = logging.getLogger('yahoo_daily_data')
    logger.info('=================START SCRIPT yahoo_daily_data ================= ')
    
    options = Options()
    options.use_chromium=True
    #options.add_argument("headless")
    options.add_argument("log-level=2")
    options.add_argument("--start-maximized")
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    tmpfile_path = os.path.join(up_onefolder,"tmpfile")
    
    options.add_experimental_option("prefs", {"download.default_directory": tmpfile_path})
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
        
        cursor.execute("SELECT ticker,exchange FROM stocks")
        result = cursor.fetchall()  
        driver = webdriver.Edge(service = service, options = options)
        if result is not None:      
            for x in result:
                ticker_xidx = x[0]+"."+x[1]
                txt_ticker = x[0]
                
                # ticker_xidx = 'PANI.XIDX'
                # txt_ticker = 'PANI'
                print('=== Populating Daily Stock Price for '+ txt_ticker)
                if debug == True :
                    print('https://finance.yahoo.com/quote/'+ txt_ticker +'.JK/history?p='+ txt_ticker +'.JK')
          
            
                url='https://finance.yahoo.com/quote/'+ txt_ticker +'.JK/history?p='+ txt_ticker + '.JK'
                
                # ticker_xidx ='BELI.XIDX'
                # txt_ticker = 'BELI'
                # url='https://finance.yahoo.com/quote/ITMG.JK/history?p=BELI.JK'
                driver.get(url)

                time.sleep(1)
               
                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                
                tbl_hist_data_xpath = '//*[@id="nimbus-app"]/section/section/section/article/div[1]/div[3]/table'
                tbl_hist_data_xpath = '//*[@id="nimbus-app"]/section/section/section/article/div[1]/div[3]/table'
                try:
                    tbl_hist_data = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, tbl_hist_data_xpath))) 
                    if tbl_hist_data is not None:
                        print("table ketemu")
                        # th_datas = tbl_hist_data.find_elements(By.TAG_NAME,"th")
                        # print(th_datas[0].text)
                        # print(th_datas[1].text)
                        # print(th_datas[2].text)
                        # print(th_datas[3].text)
                        # print(th_datas[4].text)
                        # print(th_datas[5].text)
                        # print(th_datas[6].text)
                        # print("jumlah header " + str(len(th_datas)))  
                        
                           #get existing record from db
                        query = """ select ticker, date_format(now(),'%Y-%m-%d') as today_date,  date_format(date,'%Y-%m-%d') as existing_lastdate, datediff(now(),date) as selisih, """
                        query = query + """ date_format(date_sub(now(), INTERVAL 1 day),'%Y-%m-%d') as today_minus1,  """
                        query = query + """ date_format(date_add(date, INTERVAL 1 day),'%Y-%m-%d') as lastday_plus1 from stock_daily where ticker = %s order by date desc limit 1 """
                        
                        cursor.execute(query,(ticker_xidx,))
                        result = cursor.fetchall()
                        rc = cursor.rowcount
                        if rc>0:
                            for res in result:
                                ticker_dt = res[0]
                                today_date = res[1]
                                existing_lastdate = res[2]
                                selisih = res[3]
                                today_minus1 = res[4]
                                lastday_plus1 = res[5]
  
                            tr_datas = tbl_hist_data.find_elements(By.TAG_NAME,"tr")
                            print("jumlah row ", str(len(tr_datas)))    
                            for tr_data in tr_datas:
                                td_datas = []
                                td_datas = tr_data.find_elements(By.TAG_NAME,"td")
                                print("jumlah td " + str(len(td_datas)))  
                                if len(td_datas) > 2:
                                    print(td_datas[0].text)
                                    fmt_date = parser.parse(td_datas[0].text)
                                    print(fmt_date)
                                    
                                    dt_open = cleansing_data(td_datas[1].text)
                                    dt_high = cleansing_data(td_datas[2].text)
                                    dt_low = cleansing_data(td_datas[3].text)
                                    dt_close = cleansing_data(td_datas[4].text)
                                    dt_adj_close = cleansing_data(td_datas[5].text)
                                    dt_vol =  cleansing_data(td_datas[6].text)
                                    
                                    print(dt_open)
                                    print(dt_high)
                                    print(dt_low)
                                    print(dt_close)
                                    print(dt_adj_close)
                                    print(dt_vol)

                                    if fmt_date > parser.parse(existing_lastdate):
                                        qry = """INSERT INTO stock_daily (ticker,open,high,low,close,adj_close,volume, exchange,date,updated_at,created_at)"""
                                        qry = qry + """ VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now()) """
                                        print(qry)
                                        res= cursor.execute(qry,(ticker_xidx,dt_open,dt_high,dt_low,dt_close,dt_adj_close,dt_vol,'XIDX', fmt_date))
                                        conn.commit()
                                    else:
                                        break
                        else:
                            tr_datas = tbl_hist_data.find_elements(By.TAG_NAME,"tr")
                            print("jumlah row ", str(len(tr_datas)))    
                            for tr_data in tr_datas:
                                td_datas = []
                                td_datas = tr_data.find_elements(By.TAG_NAME,"td")
                                print("jumlah td " + str(len(td_datas)))  
                                if len(td_datas) > 2:
                                    print(td_datas[0].text)
                                    fmt_date = parser.parse(td_datas[0].text)
                                    print(fmt_date)
                                    
                                    dt_open = cleansing_data(td_datas[1].text)
                                    dt_high = cleansing_data(td_datas[2].text)
                                    dt_low = cleansing_data(td_datas[3].text)
                                    dt_close = cleansing_data(td_datas[4].text)
                                    dt_adj_close = cleansing_data(td_datas[5].text)
                                    dt_vol =  cleansing_data(td_datas[6].text)
                                    
                                    print(dt_open)
                                    print(dt_high)
                                    print(dt_low)
                                    print(dt_close)
                                    print(dt_adj_close)
                                    print(dt_vol)

                                    
                                    qry = """INSERT INTO stock_daily (ticker,open,high,low,close,adj_close,volume, exchange,date,updated_at,created_at)"""
                                    qry = qry + """ VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now()) """
                                    print(qry)
                                    res= cursor.execute(qry,(ticker_xidx,dt_open,dt_high,dt_low,dt_close,dt_adj_close,dt_vol,'XIDX', fmt_date))
                                    conn.commit()
                                
                        #time.sleep(30)
           
                                
                except Exception as ex:
                    print('Error on getting ' + txt_ticker + ' data caught on: ' + str(ex) ) 
                    logger.error('Error on getting ' + txt_ticker + ' data caught on: ' + str(ex) )  
                      
                    pass
                
                

             
                            
                
    
    except mysql.connector.Error as ex:
        print('Mysql Generic Error caught on: ' + str(ex))
        try:
            print(f"MySQL Generic Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            return None
        except IndexError:
            print (f"MySQL Index Error: %s",str(ex))
            return None
    except Exception as ex:
        print('Exception Error caught on: ' + str(ex) )
        
        return None
    finally:
        conn.close
        driver.quit()
        
if __name__ == "__main__":
    update_daily_stock_price()
