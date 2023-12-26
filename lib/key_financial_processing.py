import MySQLdb
from datetime import datetime
from decimal import Decimal

from configparser import ConfigParser

debug = True
config = ConfigParser()
config.read('./conf/config.ini')


def get_last_price(cursor,txt_ticker):
    qry= " select last_price from stock_intraday where ticker = %s "
    qry = qry + " order by updated_at desc limit 1 "
    print(qry)
    
    cursor.execute(qry,(txt_ticker,))
    rows = cursor.fetchone() 
    print(txt_ticker)
    if cursor.rowcount > 0:
        if debug is True:
           print(" Last Price : "+ str(rows[0]) )
    else:
        print("no data")
    
    return rows[0]
 
def get_finance_value(cursor, table_name, txt_ticker, txt_finance_date, finance_key):
    
    if table_name == 'stock_fin_inc_stat_quarter':  
       
        qry = "select max(DATE_FORMAT(finance_date,'%%Y')) from stock_fin_inc_stat_quarter "
        qry = qry + "where ticker = %s and txt_header <> 'TTM' "
        qry = qry + "and finance_key = %s "  #'Net Income Common Stockholders'
        
        cursor.execute(qry,(txt_ticker,finance_key))
        
        rows = cursor.fetchone() 
        max_year = rows[0]
        
        val_finance_date = str(txt_finance_date).split('-')
        #print("boskuuu" + val_finance_date[0] + " max_year " + max_year)
        if int(val_finance_date[0]) == int(max_year):
            qry = "select sum(finance_value) from stock_fin_inc_stat_quarter "
            qry = qry + " where ticker = %s and txt_header <> 'TTM' "
            qry = qry + " and DATE_FORMAT(finance_date,'%%Y-%%m') <= DATE_FORMAT(%s,'%%Y-%%m') "  
            qry = qry + " and DATE_FORMAT(finance_date,'%%Y') = %s " #max_year
            qry = qry + " and finance_key = %s " #'Net Income Common Stockholders'
            cursor.execute(qry,(txt_ticker,txt_finance_date,max_year,finance_key))
            rows = cursor.fetchone() 
            txt_finance_value = rows[0]
        
      
        if int(val_finance_date[0]) == int(max_year)-1: 
            print(" Tablename " + table_name+" val_finance_date[1] : "+ val_finance_date[1])
           
            if int(val_finance_date[1]) == 12:
                
                #print(" INI YANG 12 isi int(val_finance_date[1]) : " + str(val_finance_date[1]))
                
                qry = "select finance_value from stock_fin_inc_stat_year"
                qry = qry + " where ticker = %s and txt_header <> 'TTM' "
                qry = qry + " and finance_key = %s "
                qry = qry + " and finance_date=%s "
                
                cursor.execute(qry,(txt_ticker,finance_key, txt_finance_date))
                rows = cursor.fetchone() 
                txt_finance_value = rows[0]
                
            if int(val_finance_date[1]) == 9 or int(val_finance_date[1]) == 3:
                
                #print(" INI YANG 9 or 3 Masuk sini isi int(val_finance_date[1]) : " + str(val_finance_date[1]))
                
                qry = "select sum(finance_value) from stock_fin_inc_stat_quarter "
                qry = qry + " where ticker = %s and txt_header <> 'TTM' "
                qry = qry + " and DATE_FORMAT(finance_date,'%%Y-%%m') <= DATE_FORMAT(%s,'%%Y-%%m') "  
                qry = qry + " and DATE_FORMAT(finance_date,'%%Y') = %s " #max_year-1
                qry = qry + " and finance_key = %s " #'Net Income Common Stockholders'
                cursor.execute(qry,(txt_ticker,txt_finance_date,int(max_year)-1,finance_key))
                rows = cursor.fetchone() 
                if cursor.rowcount > 0:
                    txt_finance_value = rows[0]
                    
    else:
        qry = "select finance_value from "+ table_name +" where finance_key = %s and finance_date = %s and ticker = %s limit 1"
        print(qry)
        cursor.execute(qry,(finance_key,txt_finance_date, txt_ticker))
        rows = cursor.fetchone() 
        txt_finance_value = rows[0]
    return txt_finance_value

def calculate_ttm(txt_ticker,txt_finance_date, txt_net_income_stakeholder):
    val_finance_date = str(txt_finance_date).split('-')
    month = int(val_finance_date[1])
    if month == 12:
        ttm_value = txt_net_income_stakeholder
    if month == 9:
        ttm_value = (txt_net_income_stakeholder/3)*4
    if month == 6:
        ttm_value = (txt_net_income_stakeholder/2)*4
    if month == 3:
        ttm_value = (txt_net_income_stakeholder)*4
    
    return ttm_value
    
          
def update_key_financial_records(conn,val_ticker,val_finance_date):
    
    cursor = conn.cursor()
    txt_share_issued = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Share Issued')
    #txt last price ini kalau bisa ambil pada saat tanggal yang ditentukan
    txt_last_price = get_last_price(cursor,val_ticker)
    txt_stockholders_equity = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Stockholders\' Equity')
    
    txt_total_liabilities = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Total Liabilities Net Minority Interest')
    txt_current_liabilities = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Current Liabilities')
    txt_non_current_liabilities = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Total Non Current Liabilities Net minority interest')
    
    txt_non_current_assets = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Total non-current assets')
    txt_current_assets = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Current Assets')
    txt_total_assets = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Total Assets')
    txt_net_income_stakeholders = get_finance_value(cursor,'stock_fin_inc_stat_quarter',val_ticker,val_finance_date,'Net Income Common Stockholders')
    
    txt_net_income_ttm = calculate_ttm(val_ticker,val_finance_date,txt_net_income_stakeholders)
    #harus ada calculation untuk USD vs IDR, di txt_book_value dan juga rate usd to idr
    
    txt_book_value = round(( (txt_stockholders_equity*1000)/(txt_share_issued*1000) )*15480,2)
    
 
    txt_price_to_book_value = round((txt_last_price/txt_book_value),2)
    print("txt_last_price " + str(txt_last_price) + " txt_book_value "  + str(txt_book_value) + " round((txt_last_price/txt_book_value),2) : " + str(round((txt_last_price/txt_book_value),2)) )
    # print(" txt_share_issued: " + str(txt_share_issued) + " txt_last_price  :" + str(txt_last_price) + " txt_stockholders equyity  :" + str(txt_stockholders_equity) + " txt_total_liabilities   :" + str(txt_total_liabilities))
    
    
    qry = " update key_financials "
    qry = qry + " set share_issued=%s, "
    qry = qry + " price=%s, "
    qry = qry + " stockholders_equity=%s, "
    
    qry = qry + " total_liabilities=%s, "
    qry = qry + " current_liabilities=%s, "
    qry = qry + " non_current_liabilities=%s, "
    
    qry = qry + " non_current_assets=%s, "
    qry = qry + " current_assets=%s, "
    qry = qry + " total_assets=%s, "
    qry = qry + " net_income_stakeholders=%s, "
    qry = qry + " net_income_ttm=%s, "
    qry = qry + " book_value=%s, "
    qry = qry + " price_to_book_value=%s "
    
    qry = qry + " where ticker=%s "
    qry = qry + " and finance_date =%s "
    
    cursor.execute(qry,(txt_share_issued,txt_last_price,txt_stockholders_equity,txt_total_liabilities,txt_current_liabilities,txt_non_current_liabilities,txt_non_current_assets,
                        txt_current_assets,txt_total_assets,txt_net_income_stakeholders,txt_net_income_ttm,txt_book_value, round((txt_last_price/txt_book_value),2) , val_ticker,val_finance_date))
    conn.commit() 

def key_financial_processing():
    conn = MySQLdb.connect(
        host=config.get('db_connection', 'host'),
        user=config.get('db_connection', 'user'),
        password=config.get('db_connection', 'pwd'),
        database=config.get('db_connection', 'db'),
        auth_plugin=config.get('db_connection', 'auth')
        # host="localhost",
        # user="root",
        # password="password",
        # database="db_api",
        # auth_plugin='mysql_native_password'
        )
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ticker,exchange FROM stocks")
        stocklists = cursor.fetchall() 
        
        if stocklists is not None:   
            for x in stocklists:
                txt_ticker = x[0]
                txt_ticker = 'ABMM'
               
                
                qry = " select bs.ticker, bs.finance_key,finance_value, finance_date,txt_header from stock_fin_bal_sheet_quarter bs "
                qry = qry + " where bs.ticker= %s "
                qry = qry + " and bs.txt_header <> 'TTM' "
                qry = qry + " and bs.finance_key = 'Total Assets' "
                qry = qry + " order by bs.id "
                
                cursor.execute(qry,(txt_ticker,))
                fin_bal_sheet = cursor.fetchall() 
               
                if fin_bal_sheet is not None:
                    for y in fin_bal_sheet:
                        bs_ticker = y[0]
                        bs_finance_key = y[1]
                        bs_finance_value = y[2]
                        bs_finance_date = y[3]
                        bs_txt_header = y[4]
                    
                        qry = " select count(*) rowexist from db_api.key_financials where ticker= %s and finance_date = %s and total_assets is not null" 
                        cursor.execute(qry,(bs_ticker,bs_finance_date))
                        numrow = cursor.fetchone()  
                        print("numrow ", numrow[0])
                        #if norecord
                        if numrow[0]== 0:
                            if debug == True:
                                print("Jumlah Row : " + str(numrow[0])  + " INSERT " + bs_ticker + " " + str(bs_finance_date)+ " " + str(bs_finance_key))
                            
                            qry = "INSERT INTO key_financials(ticker, "
                            qry = qry + " total_assets, "
                            qry = qry + " finance_date, "
                            qry = qry + " txt_header, "
                            qry = qry + " share_issued, "
                            qry = qry + " price, "
                            qry = qry + " stockholders_equity, "
                            qry = qry + " net_income_stakeholders, "
                            qry = qry + " net_income_ttm, "
                            qry = qry + " book_value, "
                            qry = qry + " price_to_book_value, "
                            qry = qry + " price_to_book_value_avg, "
                            qry = qry + " price_earning_ratio,"
                            qry = qry + " price_earning_ratio_avg, "
                            qry = qry + " earning_per_share, "
                            qry = qry + " return_on_equity, "
                            qry = qry + " return_on_equity_avg, "
                            qry = qry + " total_liabilities, "
                            qry = qry + " current_liabilities, "
                            qry = qry + " non_current_liabilities, "
                            qry = qry + " der, "
                            qry = qry + " current_assets, "
                            qry = qry + " cash_and_equivalents,"
                            qry = qry + " non_current_assets, "
                            qry = qry + " url_to_chart,"
                            qry = qry + " remarks, "
                            qry = qry + " flag, "
                            qry = qry + " created_at,"
                            qry = qry + " updated_at)"
                            qry = qry + " VALUES (%s,%s,%s,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'','','',now(),now()) "
                            cursor.execute(qry,(bs_ticker,bs_finance_value,bs_finance_date,bs_txt_header))
                            conn.commit()    

                            update_key_financial_records(conn,bs_ticker,bs_finance_date)
                           
                        
                        if numrow[0] == 1:
                            if debug == True:
                                print("Jumlah Row : " + str(numrow[0])  + " UPDATE " + bs_ticker + " " + str(bs_finance_date)+ " " + str(bs_finance_key)+ " " + str(bs_finance_value) )
                            # jika total_assets sudah ada di update
                            update_key_financial_records(conn,bs_ticker,bs_finance_date) 
                        
                    
                        
 
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

def main():
    key_financial_processing()
    
if __name__ == '__main__':
    main()