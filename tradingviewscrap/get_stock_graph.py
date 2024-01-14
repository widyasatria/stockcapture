import os, time, MySQLdb
from pathlib import Path
from datetime import datetime
from configparser import ConfigParser
from pywinauto.application import Application
from pywinauto import mouse
import requests
#requires PIL
from PIL import ImageGrab
from pywinauto import mouse
from time import gmtime, strftime


debug = True


def upload_graph(url, fname,ticker, username, password):

    
    values = {'ticker': ticker}
    files = {'file': open(fname, 'rb')}
    
    session = requests.Session()
    session.auth = (username, password)
    response = session.post(url,files=files,data=values)
   
    return response
    
def get_stock_graph():

    start_time = datetime.now()
        
    #requirement selenium versi 4.13.0
    #ms edge webdriver : https://msedgedriver.azureedge.net/119.0.2151.72/edgedriver_win64.zip
    
    # parameter executable_path ini sudah tidak di bisa di pakai di selenium versi 4, caranya ketik di command prompt echo %Path% untuk mengetahui existing environment variable
    # kemudian copy msedge webdriver ke salah satu path yang terdaftar.
    
    # driver = webdriver.Edge(executable_path=r'C:\Users\wardians\stockcapture\msedgedriver.exe')
    # references : https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/ie-mode?tabs=python
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    config_path = os.path.join(up_onefolder,"conf")
    conf_file = os.path.join(config_path,"config.ini")
    
    config = ConfigParser()
    config.read(conf_file)

    conn = MySQLdb.connect(
    # host="localhost",
    # user="root",
    # password="password",
    # database="db_api",
    # auth_plugin='mysql_native_password'
    host=config.get('db_connection', 'host'),
    user=config.get('db_connection', 'user'),
    password=config.get('db_connection', 'pwd'),
    database=config.get('db_connection', 'db'),
    auth_plugin=config.get('db_connection', 'auth')
    )
    
    cursor = conn.cursor()
    try:
        thisfolder = path.parent.absolute()
        screenshotfolder = os.path.join(thisfolder,"screenshots")
        
        # print(thisfolder)
        cursor.execute("SELECT ticker FROM stocks order by stock_fin_bal_sheet_quarter")
        result = cursor.fetchall()  
    
        if result is not None:   
            app=Application(backend="uia").start(cmd_line=u'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',wait_for_idle=False)
            app.connect(title=u'New tab - Work - Microsoft​ Edge',found_index=0) #supaya windows bisa dikenali pastikan copy title dari UI Spy
            window = app.top_window()   
            AppBar = window.child_window(title=u'App bar', auto_id="view_1000", control_type="ToolBar")
            #AppBar.print_control_identifiers()
            search_address = AppBar.child_window(auto_id="view_1021", control_type="Edit")
            
            for x in result:
                if debug == True :
                    print('https://id.tradingview.com/chart/evADUI5b/?symbol='+x[0])
                
                txt_ticker = x[0]
                url='https://id.tradingview.com/chart/evADUI5b/?symbol=IDX%3A'+txt_ticker
                #IDX%3AITMG ini equal dengan 
                # https://id.tradingview.com/chart/evADUI5b/?symbol=IDX:ITMG
                
               
                search_address.set_edit_text(url)
                search_address.type_keys('{ENTER}')
                time.sleep(5)
                mouse.move(coords=(1381, 569))

                left = 61
                top = 152
                right = 1454
                bottom = 880
                # Capture the entire screen
                screenshot = ImageGrab.grab()
                # Crop the captured image to the desired area
                cropped_screenshot = screenshot.crop((left, top, right, bottom))
                # Save the cropped image
                time_create = strftime("%Y-%m-%d_%H%M%S", gmtime())
                fname = txt_ticker + "_" + time_create + ".png"
                print(fname)
                screenshotfile = os.path.join(screenshotfolder, fname)
                cropped_screenshot.save(screenshotfile)
                
                upload_url = config.get('upload_api', 'upload_url')
                username = config.get('upload_api', 'api_user')
                password = config.get('upload_api', 'api_password')
                
                response = upload_graph(url=upload_url , fname=screenshotfile,ticker=txt_ticker,username=username,password=password)
                
                if debug == True:
                    print("Status Code", response.status_code)
                    print("JSON Response ", response.json())
                
                if response.status_code < 400:
                    if(os.path.isfile(screenshotfile)):
                        #os.remove() function to remove the file
                        # Not keeping the files at the worker
                        os.remove(screenshotfile)
                        if debug == True:
                            #
                            print("File Deleted successfully")
                    else:
                        if debug == True:
                            print("File does not exist")
                
            


              
                # break
            
       
      
    
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
    get_stock_graph()