from selenium import webdriver 
import requests
import urllib3
import ssl
from webdriver_manager.chrome import ChromeDriverManager # Automatically download the web driver binaries
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By # Util that helps to select elements with XPath
import csv # CSV library that helps us save our result

#options = Options() 
#options.headless = True # Run selenium under headless mode
 
#driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install())) # Initialize the driver instance


class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session


def main():
    url1="https://www.google.com/finance/quote/PTBA:IDX"
    url2="https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue"
    r = get_legacy_session().get(url1)
    pokemons = r.find_elements(By.XPATH, "//*[@id='yDmH0d']/c-wiz[2]/div/div[4]/div/main/div[1]/div[1]/div")



if __name__ == "__main__":
    main()