
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

import MySQLdb
from datetime import datetime
from decimal import Decimal
import csv
# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

debug = True

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
    
    options = Options()
    options.use_chromium=True
    options.add_argument("headless")
    options.add_argument("log-level=2")
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    tmpfile_path = os.path.join(up_onefolder,"tmpfile")
    
    options.add_experimental_option("prefs", {"download.default_directory": tmpfile_path})
    service = Service(verbose = False)
    
    
   
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
    
    download_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a/span'
    
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
                #Default Annual are openned
                #Quarterly clickable, Expandall clickable
              
                driver.implicitly_wait(4)
                download_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a'
                driver.find_element(By.XPATH,download_xpath).click()
                
                fname = os.path.join(tmpfile_path,txt_ticker+'.JK.csv')
                time.sleep(4)
               
                #get existing record from db
                query = """ select ticker, date_format(now(),'%%Y-%%m-%%d') as today_date,  date_format(date,'%%Y-%%m-%%d') as existing_lastdate, datediff(now(),date) as selisih, """
                query = query + """ date_format(date_sub(now(), INTERVAL 1 day),'%%Y-%%m-%%d') as today_minus1,  """
                query = query + """ date_format(date_add(date, INTERVAL 1 day),'%%Y-%%m-%%d') as lastday_plus1 from stock_daily where ticker = %s order by date desc limit 1 """
                
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
                            
                with open(fname, newline='') as csvfile:
                    stockprices = csv.reader(csvfile, delimiter=',', quotechar='|')
                    t=1
                    bool_format = False
                    for row in stockprices:
                        if t==1:
                            if str(row[0]) =='Date' and str(row[1])=='Open' and str(row[2])=='High' and str(row[3])=='Low' and str(row[4])=='Close' and str(row[5])=='Adj Close' and str(row[6])=='Volume':
                                bool_format = True    
                            else :
                                bool_format = False
                                print (" CSV Format is not match stopping operation")
                                break
                        if t>=2 and bool_format == True :
                            # print(str(t) + " " + str(row))
                         
                            
                            #di update terus sampe hari ini jika ada
                            if (row[0] > existing_lastdate):
                               print("jika row 0 > dari existing last date", row[0] > existing_lastdate )
                               print("row 0 : " + str(row[0]) + " existing last date : " + str(existing_lastdate))     
                               
                               qry = """INSERT INTO stock_daily (ticker,open,high,low,close,volume,adj_high,adj_low,adj_close,adj_open,adj_volume,split_factor,dividend,exchange,date,updated_at,created_at)"""
                               qry = qry + """ VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now()) """
                              
                               res= cursor.execute(qry,(ticker_xidx,isnull(row[1]),isnull(row[2]),isnull(row[3]),isnull(row[4]),isnull(row[6]),0,0,isnull(row[5]),0,0,1,0,'XIDX',row[0], ))
                               
                               conn.commit()
                               
                        t=t+1
                        
                #delete file after processing
                if (os.path.exists(fname)):
                    os.remove(fname)
               
                
                #break
    
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
    finally:
        conn.close
        driver.quit()
        
if __name__ == "__main__":
    update_daily_stock_price()
