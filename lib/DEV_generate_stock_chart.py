from pathlib import Path
import os, MySQLdb
from configparser import ConfigParser

import pandas as pd
#from pandas import DataFrame
from lightweight_charts import Chart

debug = True

def main():
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    config_path = os.path.join(up_onefolder,"conf")
    conf_file = os.path.join(config_path,"config.ini")

    print(conf_file)
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
        chart = Chart()
        
        
        sql_query = pd.read_sql_query ('''
                               select id,ticker, date, open, high, low, close,volume from db_api.stock_daily where ticker='ABMM.XIDX' order by id
                               ''', conn)
        sql_query = pd.read_sql_query ('''
                               select id,ticker, date, FORMAT(open,'#.0.00') as open, FORMAT(high,'#.0.00') as high,FORMAT(low,'#.0.00') as low,FORMAT(close,'#.0.00') as close,volume from db_api.stock_daily where ticker='ABMM.XIDX' order by id
                               ''', conn)

        df2 = pd.DataFrame(sql_query, columns = ['id', 'date','open','high','low','close','volume'])
        print (df2)
        
        path = Path(__file__)
        thisfolder = path.parent.absolute()
        thefile = os.path.join(thisfolder,"ohlcv.csv")
        print(thefile)
        df = pd.read_csv(thefile)
        print(df)
        
    
        chart.set(df)
        print(chart.data)
       
        
    
        chart.show(block=True)
    
        # cursor.execute("select id,ticker, date, open, high, low,close,volume from db_api.stock_daily where ticker='ABMM.XIDX'")
        # result = cursor.fetchall()  
      
        
        # if result is not None:      
        #     for x in result:
        #         if debug == True :
        #             print("ticker : " + str(x[1]))
                    
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

        
if __name__ == "__main__":
    main()