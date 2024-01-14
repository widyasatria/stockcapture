from pathlib import Path
import os
from configparser import ConfigParser

def get_config():
    path = Path(__file__)
    thisfolder = path.parent.absolute()
    conf_file = os.path.join(thisfolder,"config.ini")
    print(conf_file)
    config = ConfigParser()
    config.read(conf_file)

    db_host=config.get('db_connection', 'host'),
    db_user=config.get('db_connection', 'user'),
    db_password=config.get('db_connection', 'pwd'),
    database=config.get('db_connection', 'db'),
    db_auth_plugin=config.get('db_connection', 'auth')
    
    return db_host, db_user, db_password, database, db_auth_plugin