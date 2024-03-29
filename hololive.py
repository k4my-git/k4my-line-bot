import time

import requests
from bs4 import BeautifulSoup as bs
from youtubesearchpython import *

def scrape():
    print("hololive")
    global urls, times, img, icons
    link = 'https://schedule.hololive.tv/'

    res = requests.get(link)
    try:
        soup = bs(res.text, "lxml")
    except Exception:
        soup = bs(res.text, "html5lib")

    data = []

    for ele in soup.select('.col-6.col-sm-4.col-md-3'):  # ('a[style*="solid"]'):
        if 'border: 3px red' in str(ele):
            for y_url in ele.select('a[class=thumbnail]'):
                urls = y_url['href']
            #for y_time in ele.select('div[class*=col-5]'):
            #    times = y_time.get_text().replace(" ", "").replace("\n", "") + "～"
            #for y_name in ele.select('div[class*=name]'):
                #names = y_name.get_text().replace(" ", "").replace("\n", "")
            for thumbnail in ele.select('div[class*=col-12] > img'):
                img = thumbnail['src']
            count = 0
            for y_icon in ele.select('div[class*=col-xl] > img'):
                if count == 0:
                    icons = y_icon['src']
                    count += 1

            time.sleep(1)
            print(urls)
            y_data = youtubes(urls)

            data.append(dict(url=urls, name=y_data['name'], time="times", image=img, icon=icons, title=y_data['title'],
                            count=y_data['viewcount'], chlink=y_data['chlink']))
    # if not data:
    #     return None
    # else:
    #     
    return flexdata(data)


def youtubes(url):
    videoinfo = Video.getInfo(url)
    title = videoinfo["title"]
    viewcount = videoinfo["viewCount"]["text"] + "views"
    name = videoinfo["channel"]["name"]
    chlink = videoinfo["channel"]["link"]
    y_data = dict(title=title, viewcount=viewcount, name=name, chlink=chlink)

    return y_data


def flexdata(datas):
    contents = []
    for data in datas:
        template = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": data["image"],
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": data["url"]
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "contents": [
                            {
                                "type": "span",
                                "text": data["title"]
                            }
                        ],
                        "weight": "bold",
                        "size": "xl",
                        "wrap": False
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "icon",
                                "size": "md",
                                "url": 'https://schedule.hololive.tv/dist/images/icons/youtube.png',
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": data["time"],
                                "size": "md",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": data["count"],
                                "align": "center"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "image",
                                "url": data["icon"],
                                "aspectMode": "cover",
                                "size": "full"
                            }
                        ],
                        "cornerRadius": "100px",
                        "width": "72px",
                        "height": "72px",
                        "action": {
                            "type": "uri",
                            "uri": data["chlink"]
                        }
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "contents": [
                                    {
                                        "type": "span",
                                        "text": data["name"]
                                    },
                                ],
                                "margin": "xxl",
                                "size": "xl",
                                "align": "center",
                                "wrap": True
                            }
                        ]
                    }
                ],
                "spacing": "xl",
                "paddingAll": "20px"
            }
        }
        contents.append(template)
    return contents
