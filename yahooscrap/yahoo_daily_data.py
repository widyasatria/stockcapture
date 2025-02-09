
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
                print('=== Populating Daily Stock Price for '+ txt_ticker)
                if debug == True :
                    print('https://finance.yahoo.com/quote/'+x[0]+'.JK/history?p='+x[0]+'.JK')
          
            
                url='https://finance.yahoo.com/quote/'+x[0]+'.JK/history?p='+x[0]+'.JK'
                
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
                        
                        tr_datas = tbl_hist_data.find_elements(By.TAG_NAME,"tr")
                        print("jumlah row " + str(len(tr_datas)))    
                        for tr_data in tr_datas:
                            td_datas = tr_data.find_elements(By.TAG_NAME,"td")
                            if debug==True:
                                print("jumlah td " + str(len(td_datas)))   
                            
                            for td_data in td_datas:
                                print(td_data.text) 
                            
                            
                        time.sleep(30)
           
                                
                except Exception as ex:
                    print('Error on getting ' + txt_ticker + ' data caught on: ' + str(ex) ) 
                    logger.error('Error on getting ' + txt_ticker + ' data caught on: ' + str(ex) )  
                      
                    pass
                
                

                #get existing record from db
                query = """ select ticker, date_format(now(),'%Y-%m-%d') as today_date,  date_format(date,'%Y-%m-%d') as existing_lastdate, datediff(now(),date) as selisih, """
                query = query + """ date_format(date_sub(now(), INTERVAL 1 day),'%Y-%m-%d') as today_minus1,  """
                query = query + """ date_format(date_add(date, INTERVAL 1 day),'%Y-%m-%d') as lastday_plus1 from stock_daily where ticker = %s order by date desc limit 1 """
                
                cursor.execute(query,(ticker_xidx,))
                result = cursor.fetchall()
                rc = cursor.rowcount
                if rc>0:
                    for row in result:
                        ticker_dt = row[0]
                        today_date = row[1]
                        existing_lastdate = row[2]
                        selisih = row[3]
                        today_minus1 = row[4]
                        lastday_plus1 = row[5]
                            
                # with open(fname, newline='') as csvfile:
                #     stockprices = csv.reader(csvfile, delimiter=',', quotechar='|')
                #     t=1
                #     bool_format = False
                #     for row in stockprices:
                #         if t==1:
                #             if str(row[0]) =='Date' and str(row[1])=='Open' and str(row[2])=='High' and str(row[3])=='Low' and str(row[4])=='Close' and str(row[5])=='Adj Close' and str(row[6])=='Volume':
                #                 bool_format = True    
                #             else :
                #                 bool_format = False
                #                 print (" CSV Format is not match stopping operation")
                #                 break
                #         if t>=2 and bool_format == True :
                #             # print(str(t) + " " + str(row))
                         
                            
                #             #di update terus sampe hari ini jika ada
                #             if (row[0] > existing_lastdate):
                #                print("jika row 0 > dari existing last date", row[0] > existing_lastdate )
                #                print("row 0 : " + str(row[0]) + " existing last date : " + str(existing_lastdate))     
                               
                #                qry = """INSERT INTO stock_daily (ticker,open,high,low,close,volume,adj_high,adj_low,adj_close,adj_open,adj_volume,split_factor,dividend,exchange,date,updated_at,created_at)"""
                #                qry = qry + """ VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now()) """
                              
                #                res= cursor.execute(qry,(ticker_xidx,isnull(row[1]),isnull(row[2]),isnull(row[3]),isnull(row[4]),isnull(row[6]),0,0,isnull(row[5]),0,0,1,0,'XIDX',row[0], ))
                               
                #                conn.commit()
                               
                        t=t+1
                        
           
                
                #break
    
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
