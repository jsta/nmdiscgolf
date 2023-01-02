import re
import twitter
import requests
import datetime
import pandas as pd
from colorama import Fore
from bs4 import BeautifulSoup

import config

tweet = True
interactive = False


def get_tourneys(date=None):
    if date is None:
        date_raw = datetime.date.today()
        date = str(date_raw)
    else:
        date_raw = datetime.datetime.strptime(date, "%Y-%m-%d")

    end_date = str(
        date_raw.replace(year=int(datetime.datetime.strftime(date_raw, "%Y")) + 1)
    ).split(" ")[0]

    baseurl = (
        "https://www.pdga.com/tour/search?OfficialName=&td=&date_filter%5Bmin%5D%5Bdate%5D="
        + date
        + "&date_filter%5Bmax%5D%5Bdate%5D="
        + end_date
        + "&State%5B%5D=NM"
    )

    response = requests.get(baseurl)
    soup = BeautifulSoup(response.text, "html.parser")

    locations = soup.findAll("td", class_="views-field-Location")
    _get_locations = lambda x: re.findall(r'(?<=Location"\>\n)(.*)(?=\s\<\/td)', x)
    locations = [_get_locations(str(x))[0] for x in locations]

    dates = soup.findAll("td", class_="views-field-StartDate")
    _get_dates = lambda x: re.findall(r'(?<=StartDate"\>\n)(.*)(?=\s\<\/td)', x)
    dates = [_get_dates(str(x))[0] for x in dates]

    names = soup.findAll("td", class_="views-field-OfficialName")
    _get_names = lambda x: re.findall(r'(?<="\>)(.*)(?=\<\/a)', x)
    names = [_get_names(str(x))[0] for x in names]

    links = soup.findAll("td", class_="views-field-OfficialName")
    _get_link = lambda x: re.findall(r'(?<=\<a href=")(.*)(?=")', x)
    links = ["https://www.pdga.com" + _get_link(str(x))[0] for x in links]

    res = pd.DataFrame([names, dates, locations, links]).T
    res.columns = ["name", "date", "location", "link"]

    res = [" | ".join(res.iloc[i]) for i in range(0, res.shape[0])]
    res = pd.DataFrame(res, columns=["slug"])

    return res


tourneys = get_tourneys()

log = pd.read_csv("log.csv")
res = tourneys[~tourneys["slug"].isin(log["slug"])]
res = res.sample(frac=1)

## print/offer tweets
slugs = res["slug"]
print(Fore.GREEN + "Filtered: ")
print()
for slug in slugs:
    print(Fore.GREEN + slug)
    print()

if tweet is True or interactive is True:
    # api = twitter.Api(
    #     consumer_key=config.api_key,
    #     consumer_secret=config.api_secret_key,
    #     access_token_key=config.access_token_key,
    #     access_token_secret=config.access_token_secret,
    # )
    # api.VerifyCredentials()

    for i in range(len(res)):
        # status = api.PostUpdate(slug)
        # write to log
        keys = ["slug", "date"]
        slug = res.iloc[i]["slug"]
        date = str(datetime.date.today())
        d = dict(zip(keys, [slug, date]))

        d = pd.DataFrame.from_records(d, index=[0])
        log = log.append(pd.DataFrame(data=d), ignore_index=True)
        log.to_csv("log.csv", index=False)
