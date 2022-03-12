import json
from urllib.request import Request, urlopen 
import psycopg2 
from config import db_info, market_aux
import re
import argparse
 
 
# Initialize parser
parser = argparse.ArgumentParser()


parser.add_argument("-p", "--page", help = "input page number")

parser.add_argument("-nx", "--nextxpages", help = "next x pages")

args = parser.parse_args()




hostname = db_info.hostname
database = db_info.database
username = db_info.username
pwd = db_info.password
port = db_info.port

# api_key = market_aux.api_key


def put_into_database(insert_script_list):
    conn = None 
    cur = None 
    try:
        conn = psycopg2.connect(host = hostname,dbname = database, user = username, password = pwd , port = port)
        cur = conn.cursor()
        for insert_script in insert_script_list:
            cur.execute(insert_script)
        conn.commit()
        print("Database updated successfully....")
    except Exception as error:
        print(error)
    finally: 
        if cur is not None:
            cur.close() 
        if conn is not None:
            conn.close()

def get_from_database(select_script):
    conn = None 
    cur = None 
    try:
        conn = psycopg2.connect(host = hostname,dbname = database, user = username, password = pwd , port = port)
        cur = conn.cursor()
        cur.execute(select_script)
        data = cur.fetchall()
        conn.commit()
        print("Fetched from database successfully....")
    except Exception as error:
        print(error)
    finally: 
        if cur is not None:
            cur.close() 
        if conn is not None:
            conn.close()
        return data 


def get_entity_url(api_key,page,country):
    marketaux_entity_search_api_path = 'https://api.marketaux.com/v1/entity/search'
    return f'{marketaux_entity_search_api_path}?api_token={api_key}&countries={country}&page={page}'




def get_data(url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    req = Request(url)
    for key, val in hdr.items():
        req.add_header(key, val)
    response = urlopen(req)
    data = response.read()
    dict = json.loads(data)
    return dict 






def get_insert_script_for_entity(entity_dict):
    for  key , val in entity_dict.items(): 
        if isinstance(val, str):
            entity_dict[key] = entity_dict[key].replace("'","") 
    symbol = entity_dict["symbol"]
    name  = entity_dict['name']
    type =  entity_dict["type"]
    industry =  entity_dict["industry"]
    exchange =  entity_dict["exchange"]
    exchange_long =  entity_dict["exchange_long"]
    country =  entity_dict["country"]
    temp_script =  f'''INSERT INTO metadata.entity(symbol, name, type, industry, exchange, exchange_long, country) 
    VALUES ('{symbol}','{name}' , '{type}', '{industry}', '{exchange}', '{exchange_long}', '{country}') '''
    temp_script = temp_script.replace('\n', '')
    temp_script = re.sub(' +', ' ', temp_script)
    return temp_script

def get_insert_script_for_entity_meta_data(entity_meta_dict):
    for  key , val in entity_meta_dict.items(): 
        if isinstance(val, str):
            entity_meta_dict[key] = entity_meta_dict[key].replace("'","") 
    found = entity_meta_dict["found"]
    returned  = entity_meta_dict['returned']
    limit =  entity_meta_dict["limit"]
    page =  entity_meta_dict["page"]
    temp_script =  f'''INSERT INTO metadata.entity_meta_data(found, returned, "limit", page) 
    VALUES ('{found}','{returned}' , '{limit}', '{page}' )'''
    temp_script = temp_script.replace('\n', '')
    temp_script = re.sub(' +', ' ', temp_script)
    return temp_script





def do_job(pageNumber):
    country = 'in'
    insert_script_list_for_entity = []
    url  = get_entity_url(market_aux.api_key,pageNumber,country)
    data_from_marketaux = get_data(url)
    for data_entity in data_from_marketaux['data']:
        insert_script_list_for_entity.append(get_insert_script_for_entity(data_entity))
    insert_script_for_entity_meta_data =  get_insert_script_for_entity_meta_data( data_from_marketaux['meta'])
    # print(insert_script_list_for_entity[0])
    put_into_database(insert_script_list_for_entity)
    put_into_database([insert_script_for_entity_meta_data])


page_number = args.page

next_x_pages = args.nextxpages


if page_number is not None and next_x_pages is None:
    do_job(page_number)

elif next_x_pages is not None:
    select_script =  "SELECT * FROM metadata.entity_meta_data"
    data = get_from_database(select_script)
    last_page = max([int(x[-1]) for x in data])
    print(data)
    print(f"{last_page} is last page..... ")
    # print("no not like this...")
else:
    print("bhai kya kar raha hai tu")










