import time
from pywinauto.application import Application
from pywinauto import  mouse
#requires PIL
from PIL import ImageGrab
from pywinauto import mouse

# References
# https://stackoverflow.com/questions/54267715/how-to-connect-current-edge-using-pywinauto-and-input-url
# https://www.youtube.com/watch?v=6G60NYyUhNE

#pertama2 cek menggunakan 
app=Application(backend="uia").start(cmd_line=u'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',wait_for_idle=False)
app.connect(title=u'New tab - Work - Microsoft​ Edge')
window = app.top_window()
# to show parent tree
window.print_control_identifiers()
FavoriteBar = window.child_window(title="Favorites bar", auto_id="view_1045", control_type="ToolBar")
# to show parent tree
#FavoriteBar.print_control_identifiers()

AppBar = window.child_window(title=u'App bar', auto_id="view_1000", control_type="ToolBar")
#AppBar.print_control_identifiers()
search_address = AppBar.child_window(auto_id="view_1021", control_type="Edit")
#search_address.print_control_identifiers()
search_address.set_edit_text('https://id.tradingview.com/chart/evADUI5b/?symbol=ITMG')
search_address.type_keys('{ENTER}')
time.sleep(5)
#untuk memindah mouse cursor ke bar yang paling akhir supaya note tanggal hari ini keluar
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

cropped_screenshot.save("c:\\temp\\ss\\ITMG_1-12-2023.png")


#main_window.dump_tree() # print long output with control identifiers
