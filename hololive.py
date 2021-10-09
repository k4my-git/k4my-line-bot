from bs4 import BeautifulSoup as bs
import requests
import lxml,html5lib

def scrape():
    url = 'https://schedule.hololive.tv/'

    res = requests.get(url)
    try:
        soup = bs(res.text, "lxml")
    except:
    	soup = bs(res.text, "html5lib")
    
    data=[]

    for ele in soup.select('.col-6.col-sm-4.col-md-3'):#('a[style*="solid"]'):
    	if 'border: 3px red' in str(ele):
    		for y_time in ele.select('div[class*=col-5]'):
    			times = y_time.get_text().replace(" ","").replace("\n","")
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

    		data.append(dict(name=names,time=times,image=img,icon=icons))
    return flexdata(data)

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
                          "uri": "http://linecorp.com/"
                        }
                      },
                      "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                          {
                            "type": "text",
                            "text": data["name"],
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
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png",
                                "margin": "none"
                              },
                              {
                                "type": "text",
                                "text": data["time"],
                                "size": "md",
                                "margin": "md"
                              }
                            ]
                          }
                        ]
                      },
                      "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "none",
                        "contents": [
                          {
                            "type": "image",
                            "url": data["icon"],
                            "size": "md",
                            "margin": "none",
                            "aspectMode": "fit"
                          }
                        ],
                        "flex": 0,
                        "margin": "none"
                      }
                    }
        base["contents"].append(template)
    return base
