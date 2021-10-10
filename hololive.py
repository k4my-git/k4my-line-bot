from bs4 import BeautifulSoup as bs
import requests
import lxml,html5lib
from youtubesearchpython import *

def scrape():
    link = 'https://schedule.hololive.tv/'

    res = requests.get(link)
    try:
        soup = bs(res.text, "lxml")
    except:
    	soup = bs(res.text, "html5lib")
    
    data=[]

    for ele in soup.select('.col-6.col-sm-4.col-md-3'):#('a[style*="solid"]'):
    	if 'border: 3px red' in str(ele):
    		for y_url in ele.select('a[class=thumbnail]'):
    			urls = y_url['href']
    		for y_time in ele.select('div[class*=col-5]'):
    			times = y_time.get_text().replace(" ","").replace("\n","")+"～"
    			#print("start >"+times)
    		for y_name in ele.select('div[class*=name]'):
    			names = y_name.get_text().replace(" ","").replace("\n","")
    			#print("name >"+names)
    		for thumbnail in ele.select('div[class*=col-12] > img'):
    			img = thumbnail['src']
    			#print("thumbnail >"+img)
    		count = 0
    		for y_icon in ele.select('div[class*=col-xl] > img'):
    			if count == 0:
    				icons = y_icon['src']
    				count+=1
    		y_data = youtubes(urls)

    		data.append(dict(url=urls,name=y_data['name'],time=times,image=img,icon=icons,title=y_data['title'],count=y_data['viewcount'],chlink=y_data['chlink']))
    return flexdata(data)

def youtubes(url):
  #url = 'https://www.youtube.com/watch?v=9tgw2xkclFA'
  videoinfo = Video.getInfo(url)
  title = videoinfo["title"]
  viewcount = "視聴回数："+videoinfo["viewCount"]["text"]
  name = videoinfo["channel"]["name"]
  chlink = videoinfo["channel"]["link"]
  y_data = dict(title=title,viewcount=viewcount,name=name,chlink=chlink)

  return y_data

def flexdata(datas):
    base = {
            "type": "carousel",
            "contents": []
            }
    
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
                            "text": data["title"],
                            "weight": "bold",
                            "size": "xl"
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
                                "align": "end"
                              }
                            ]
                          }
                        ]
                      },
                      "footer": {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "none",
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
                            "layput": "vertical",
                            "contents": [
                              {
                                "type": "text",
                                "text": data["name"],
                                "margin": "xxl",
                                "size": "xl",
                                "align": "center"
                              }
                            ]
                          }
                        ],
                        "flex": 0,
                        "margin": "none"
                      }
                    }
        base["contents"].append(template)
    return base
