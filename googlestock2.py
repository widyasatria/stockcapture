import requests
import urllib3
import ssl
from bs4 import BeautifulSoup



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
    #sess = get_legacy_session().get("https://www.google.com/finance/quote/PTBA:IDX")
    url1="https://www.google.com/finance/quote/PTBA:IDX"
    url2="https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue"
    r = get_legacy_session().get(url1)
    #soup = BeautifulSoup(r.text, 'html.parser')
    soup = BeautifulSoup(r.text, 'html')
    print(soup)
    #print(soup.text)
    #print(soup.find_all('div'))
 
    #soup = BeautifulSoup(r.content,'html.parser')
    #print(str(soup))
    
    #print(soup.find_all('div'))
    #print(soup.getText)
    #soup.find_all("div", class_="text-5xl font-bold leading-9 md:text-[42px] md:leading-[60px] text-[#232526]")
    
    

if __name__ == "__main__":
    main()

