import requests
import MySQLdb

import time

from datetime import datetime, timedelta

api_limit = 980
debug = True

def isnull(val):
    if val is None:
        val = 0
    return val
    
def get_daily_market_data():
    
    conn = MySQLdb.connect(
        host="localhost",
        user="root",
        password="password",
        database="db_api",
        auth_plugin='mysql_native_password'
        )
    
    cursor = conn.cursor()
    try:
        #disini harus ada iterasi from table stock
        cursor.execute("SELECT ticker,exchange FROM stocks")
        stocklists = cursor.fetchall()  
    
        if stocklists is not None:   
            for x in stocklists:
      
                ticker = x[0]+"."+x[1]
                
      
                query="""SELECT id, source_url,secret_key,number_of_call FROM db_api.stock_data_feed where number_of_call <= %s limit 1"""
                cursor.execute(query,(api_limit,))
                id, source_url, secret_key, number_of_call = cursor.fetchone()  
            
                if secret_key is not None:  
                    query = """ select ticker, date_format(now(),'%%Y-%%m-%%d') as today_date,  date_format(date,'%%Y-%%m-%%d') as existing_lastdate, datediff(now(),date) as selisih, """
                    query = query + """ date_format(date_sub(now(), INTERVAL 1 day),'%%Y-%%m-%%d') as today_minus1,  """
                    query = query + """ date_format(date_add(date, INTERVAL 1 day),'%%Y-%%m-%%d') as lastday_plus1 from db_api.stock_daily where ticker = %s order by date desc limit 1 """
                    
                    cursor.execute(query,(ticker,))
                    result = cursor.fetchall()
                    rc = cursor.rowcount
                    #ticker_dt, today_date,existing_lastdate, selisih, today_minus1, lastday_plus1 = cursor.fetchone()
                    
                    if debug == True:
                        print("Number of records found : " + str(rc))
                    
            
                    #jika data sudah pernah ada
                    if rc>0:
                        for row in result:
                            ticker_dt = row[0]
                            today_date = row[1]
                            existing_lastdate = row[2]
                            selisih = row[3]
                            today_minus1 = row[4]
                            lastday_plus1 = row[5]
                            
                            
                        params = {
                        'symbols' : ticker_dt,
                        'access_key': secret_key,
                        'date_from' : lastday_plus1,
                        'date_to': today_minus1,
                        'limit' : '1000'
                        }
                    
                    else:
                        #Jika belum pernah ada datanya 
                        # ambil data 3 tahun terakhir
                    
                        date_from = datetime.now() - timedelta(days=1000)
                        date_from = date_from.strftime('%Y-%m-%d')
                        
                        print(date_from)
                    
                        params = {
                        'symbols' : ticker,
                        'access_key': secret_key,
                        'date_from' : date_from,
                        'date_to': datetime.today().strftime('%Y-%m-%d'),
                        'limit' : '1000'
                        }
                        
                      
                    api_result = requests.get(source_url, params)
                        
                    api_response = api_result.json()
                    if debug == True:
                            print("Parameter to be send ", params)
                            print(" API return status code : ", api_result.status_code)  
                            if api_result.status_code != 200:
                                print(" API return content for " + ticker + " " + str(api_result.content))  
                                
                    
                    #api_response = None
                
                        
                    qry="""update db_api.stock_data_feed set number_of_call=%s where id=%s"""
                    number_of_call = number_of_call +1
                    res= cursor.execute(qry,(number_of_call,id,))
                    conn.commit()
                    cnt = 0    
                    if api_result.status_code == 200:
                        
                        for stock_data in api_response["data"]:
                            #print(f'Ticker %s has a day high of  %s on %s', stock_data['symbol'],stock_data['high'],stock_data['date'])
                            # print(stock_data['open'])
                            
                            qry = """INSERT INTO db_api.stock_daily (ticker,open,high,low,close,volume,adj_high,adj_low,adj_close,adj_open,adj_volume,split_factor,dividend,exchange,date,updated_at,created_at)"""
                            qry = qry + """ VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now()) """
                            
                            
                            t1 = stock_data['date'].split("T")
                            t2 = t1[0].split("-")
                            tanggal = datetime(int(t2[0]),int(t2[1]),int(t2[2]))
                            
                            # if debug == True:
                            #     print( "Tanggal ", tanggal)
                            # tanggal = t ime.strftime('%Y-%m-%d %H:%M:%S', stock_data['date'])
                            # print(tanggal)
                            
                            res= cursor.execute(qry,(stock_data['symbol'],stock_data['open'],stock_data['high'],stock_data['low'],stock_data['close'],isnull(stock_data['volume']),isnull(stock_data['adj_high']),isnull(stock_data['adj_low']),isnull(stock_data['adj_close']),isnull(stock_data['adj_open']),isnull(stock_data['adj_volume']),stock_data['split_factor'],stock_data['dividend'],stock_data['exchange'],tanggal, ))
                            cnt = cnt+1
                            conn.commit()
                    print (" Getting data from  :", source_url)
                    print (" Ticker : ",ticker)
                    print(" Date_to ", params)
                    print(" Number of data inserted ", cnt)            
                else:
                    print("NO API url available for this activity")
                    break
        
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
        print('Generic Error caught on: '+ ticker +' : ' + str(ex) )
        return None
    finally:
        conn.close


    
if __name__ == '__main__':
    get_daily_market_data()