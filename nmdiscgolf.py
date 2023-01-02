import re
import twitter
import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_tourneys():

    baseurl = 'https://www.pdga.com/tour/search?OfficialName=&td=&date_filter%5Bmin%5D%5Bdate%5D=2023-01-01&date_filter%5Bmax%5D%5Bdate%5D=2024-01-01&State%5B%5D=NM'

    response = requests.get(baseurl)
    soup = BeautifulSoup(response.text, 'html.parser')

    locations = soup.findAll('td', class_="views-field-Location")
    _get_locations = lambda x: re.findall(r'(?<=Location"\>\n)(.*)(?=\s\<\/td)', x)
    locations = [_get_locations(str(x))[0] for x in locations]

    dates = soup.findAll('td', class_="views-field-StartDate")
    _get_dates = lambda x: re.findall(r'(?<=StartDate"\>\n)(.*)(?=\s\<\/td)', x)
    dates = [_get_dates(str(x))[0] for x in dates]

    names = soup.findAll('td', class_="views-field-OfficialName")
    _get_names = lambda x: re.findall(r'(?<="\>)(.*)(?=\<\/a)', x)
    names = [_get_names(str(x))[0] for x in names]

    links = soup.findAll('td', class_="views-field-OfficialName")
    _get_link = lambda x: re.findall(r'(?<=\<a href=")(.*)(?=")', x)
    links = ["https://www.pdga.com" + _get_link(str(x))[0] for x in links]

    res = pd.DataFrame([names, dates, locations, links]).T
    res.columns = ["name", "date", "location", "link"]

    return res