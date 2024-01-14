import requests
from pathlib import Path, os 

user = "admin"
password="password"

path = Path(__file__)
thisfolder = path.parent.absolute()
screenshotfolder = os.path.join(thisfolder,"screenshots")
screenshotfile = os.path.join(screenshotfolder, "SMDR_2024-01-14_011209.png")
fname=""
url = 'http://127.0.0.1:8000/api/upload-file/'
values = {'ticker': 'SMDR'}
files = {'file': open(screenshotfile, 'rb')}
print(screenshotfile)
print("omigot")

session = requests.Session()
session.auth = (user, password)

response = session.post(url,files=files,data=values)

print("Status Code", response.status_code)
print("JSON Response ", response.json())
#print(x.text)