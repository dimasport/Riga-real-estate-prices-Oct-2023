#!/usr/bin/env python
# coding: utf-8

# In[174]:


import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup as bs


# In[175]:


URL_TEMPLATE = "https://www.ss.lv/lv/real-estate/flats/riga/all/sell/"


# In[176]:


r = requests.get(URL_TEMPLATE)
print(r.status_code)


# In[177]:


soup = bs(r.text, "html.parser")
parsed_data = soup.find_all('a', class_='am')


# In[178]:


parsed_data[:2]


# In[179]:


parsed_data[0].get('href')


# In[180]:


def get_link(link, time_sleep, page_num):
    
    time.sleep(time_sleep)
    link = link + 'page' + str(page_num) + '.html'
    r = requests.get(link)
    
    if r.status_code!=200:
        return 
    
    soup = bs(r.text, "html.parser")
    parsed_data = soup.find_all('a', class_='am')
    
    pars_links = []
    
    for data in parsed_data:
        pars_links.append(data.get('href'))
        
    return pars_links


# In[181]:


link_array = []
URL_TEMPLATE = "https://www.ss.lv/lv/real-estate/flats/riga/all/sell/"


# In[182]:


#have 113 pages in total (for trial run used 3 pages)
for i in tqdm(range(1,3)):
    link_array = link_array + get_link(URL_TEMPLATE, 1, i)


# In[183]:


link_array[:10]


# In[184]:


# обратите внимание, от нашего URL остался только домен, остальное мы будет добавлять из сохраненных ссылок
URL_TEMPLATE = "https://www.ss.lv"


# In[185]:


len(link_array)


# In[186]:


URL_TEMPLATE += link_array[0]


# In[187]:


r = requests.get(URL_TEMPLATE)
print('Error status', r.status_code)


# In[188]:


soup = bs(r.text, "html.parser")
# parsed_data = soup.find_all('td', class_='msga2-o pp6')


# In[189]:


parsed_data = soup.find_all('td', class_='ads_opt')
parsed_data


# In[190]:


# все данные получили
for i in parsed_data:
    print(i.get_text("|"))


# In[191]:


# теперь попробуем достать карту 
parsed_map = soup.find_all('a', class_='ads_opt_link_map')
print(parsed_map[0]['onclick'])


# In[192]:


# и тогда достанем и описание апартаментов 
parsed_text = soup.find_all('div', id='msg_div_msg')
parsed_text[0].get_text(" | ")

# обратите внимание, что в контейнере id=msg_div_msg захватывает и данные по атрибутам которые мы уже взяли, 
# это связано с принципом вложенности, в данном контейнере и находяться наши теги td


# In[193]:


# и как же без цены
parsed_price = soup.find_all('td', class_='ads_price')
parsed_price[0].get_text()


# In[194]:


# по традиции что выполняется больше 1го раза мы пишем в функцию. 
# напишем функцию в которую мы будем передавать ссылку. а все данные в ввиде массива будут приходить ответом 


# In[195]:


def get_data_link(url, time_sleep):
    
    page_array = []
    time.sleep(time_sleep)
    
    # добавляем к существующему домену
    link = "https://www.ss.lv"
    link += url
    
    r = requests.get(link)
    if r.status_code!=200:
        return 
    
    soup = bs(r.text, "html.parser")
        
    # данные 
    parsed_data = soup.find_all('td', class_='ads_opt')   
    # координаты
    parsed_map = soup.find_all('a', class_='ads_opt_link_map')   
        
    # цена
    parsed_price = soup.find_all('td', class_='ads_price')    
    # описание 
    parsed_text = soup.find_all('div', id='msg_div_msg')
    
    
    for data in parsed_data:
        page_array.append(data.get_text("|"))

    if len(parsed_map)==1:
        page_array.append(parsed_map[0]['onclick'])
    else:
        page_array.append('')
    
    page_array.append(parsed_price[0].get_text())       
    page_array.append(parsed_text[0].get_text(" | "))
    
    return page_array


# In[196]:


#data_array = []

#data_array.append(get_data_link(link_array[447], 1))


# In[197]:


data_array


# In[198]:


# запишем все данные 
data_array = []

for links in tqdm(link_array):
    # у нас будет 1470 запросов. довольно много, иногда лучше увеличить время ожидания, чем поймать бан 
    # в нашем случае парсинг + выгрузка (с тайм аутом) занимают ~1,8 сек, этого обычно достаточно достаточно
    # из опыта могу сказать что в среднем устанавливают до 500 итераций в минуту или 8.3 в секунду
    data_array.append(get_data_link(links, 0.25))


# In[199]:


len(data_array)


# In[200]:


# в части данных присутсвует дополнительное поле "удобства", добавим строку для формирования df 
# в части данных присутсвует дополнительное поле "Kadastra numurs", добавим строку для формирования df 
data_array_upd = []
for i in data_array:
    if len(i)==11:
        i.insert(8, '')
    if len(i)==12:
        i.insert(8, '')
    data_array_upd.append(i)
    
data_array_upd_1 = []
for i in data_array_upd:
    if len(i)==12:
        i.insert(8, '')
    data_array_upd_1.append(i)


# In[201]:


data_array_upd=data_array_upd_1


# In[202]:


df = pd.DataFrame(data_array_upd, columns=['city', 'district','street','rooms','area','floor','seria','house_type','kadastr_numb','facilities', 'map','price','all_data'])


# In[203]:


df.sample(2)


# In[204]:


# преступим к очистке данных


# In[205]:


df['city'].unique()


# In[206]:


df['district'].unique()


# In[207]:


df[['data_street', 'map_link']] = df['street'].str.split(pat='|', n=1 , expand=True )


# In[208]:


df = df.drop(['city','map_link','street','kadastr_numb'], axis=1)


# In[209]:


df[['cur_floor', 'max_floor']] = df['floor'].str.split(pat='/', n=1 , expand=True )


# In[210]:


df = df.drop(['floor'], axis=1)


# In[211]:


df.to_excel('df.xlsx', index=False)


# In[212]:


df['map']=df['map'].fillna('-1')


# In[213]:


def get_cord(row):
    # ищем стартовую точку 
    point_start = row['map'].find('c=') + 2
    
    first_coma = row['map'][point_start:].find(',') + 1

    second_coma = row['map'][point_start+first_coma:].find(',')
    
    cord = row['map'][point_start:point_start+first_coma+second_coma]
    
    return cord    


# In[214]:


df['cord_map'] = df.apply(get_cord, axis=1)


# In[215]:


df[['len', 'lon']] = df['cord_map'].str.split(pat=',', n=1 , expand=True )
df = df.drop(['cord_map'], axis=1)
df = df.drop(['map'], axis=1)


# In[216]:


df['area'] = df['area'].apply(lambda x: x.replace(' m²',''))


# In[217]:


df[['price_eur', 'else_price']] = df['price'].str.split(pat='(', n=1 , expand=True )


# In[218]:


df = df.drop(['price','else_price'], axis=1)


# In[219]:


df['max_floor'].unique()


# In[220]:


df[['total_floor', 'lift']] = df['max_floor'].str.split(pat='/', n=1 , expand=True )
df = df.drop(['max_floor'], axis=1)


# In[221]:


df[['price', 'currency']] = df['price_eur'].str.split(pat=' €', n=1 , expand=True )


# In[222]:


df = df.drop(['price_eur'], axis=1)


# In[223]:


df['price']=df['price'].fillna('-1')


# In[224]:


df['price'] = df['price'].apply(lambda x: x.replace(' ',''))


# In[225]:


df['lon'] = df['lon'].fillna('-1')
df['len'] = df['len'].fillna('-1')

df.loc[df['len']=='', 'len'] = '-1'
df.loc[df['lon']=='', 'lon'] = '-1'


# In[226]:


df['len'] = df['len'].apply(lambda x: x.replace(' ',''))
df['lon'] = df['lon'].apply(lambda x: x.replace(' ',''))


# In[227]:


df = df[['district','data_street','rooms','area','price','cur_floor','total_floor', 'lift', 'seria','house_type','facilities','len','lon','all_data']]


# In[228]:


df=df[df['rooms']!='Citi']


# In[229]:


df['cur_floor']=df['cur_floor'].replace('1.00', 1)


# In[230]:


df['rooms'] = df['rooms'].astype('int64')
df['area'] = df['area'].astype('float64')
df['price'] = df['price'].astype('int64')
df['cur_floor'] = df['cur_floor'].astype('int64')
df['total_floor'] = df['total_floor'].astype('int64')
df['len'] = df['len'].astype('float64')
df['lon'] = df['lon'].astype('float64')


# In[231]:


df_all_data = df['all_data']


# In[232]:


df = df.drop(['all_data'], axis=1)


# In[233]:


df['facilities'].unique()


# In[234]:


arr_facilities = ['Terase', 'Terase, Parkošanas vieta', 'Lodžija',
       'Lodžija, Parkošanas vieta', 'Parkošanas vieta', 'Balkons',
       'Balkons, Lodžija, Terase',
       'Pirts, Parkošanas vieta', 'Balkons, Parkošanas vieta',
       'Balkons, Lodžija', 'Balkons, Lodžija, Parkošanas vieta',
       'Balkons, Lodžija, Terase, Parkošanas vieta',
       'Balkons, Terase, Parkošanas vieta',
       'Lodžija, Terase, Parkošanas vieta', 'Lodžija, Terase',
       'Terase, Pirts']


# In[235]:


df['lift'] = np.where(df['lift']=='lifts',1,0)


# In[236]:


df['facilities'] = np.where(df['facilities'].isin(arr_facilities),df['facilities'],'')


# In[237]:


df.head()


# In[238]:


len(df)


# In[239]:


df=df.drop_duplicates()


# In[240]:


len(df)


# In[241]:


df.head()


# In[140]:


df.to_csv('df_for_sale_riga_11102023.csv',index=False)


# In[ ]:




