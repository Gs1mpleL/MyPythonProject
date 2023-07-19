import requests
import json


def get_html():
    html = requests.get("https://weibo.com/ajax/side/hotSearch").text
    return html


def parse_hot_news_json_data(data):
    one_hot_news_dict = {
        "title": data["word"]
    }
    one_hot_news_dict['url'] = "https://s.weibo.com/weibo?q=%23" + one_hot_news_dict["title"] + "%23"
    if 'label_name' in data:
        if data["label_name"] == '':
            one_hot_news_dict["label"] = "普"
        else:
            one_hot_news_dict["label"] = data["label_name"]
    else:
        one_hot_news_dict["label"] = "普"
    if 'realpos' in data:
        one_hot_news_dict["rank"] = data["realpos"]

    if 'category' in data:
        one_hot_news_dict["category"] = data["category"]
    return one_hot_news_dict


def parse_html(html):
    data = json.loads(html)
    parsed_list = []
    data_dict = data["data"]["realtime"]
    for one_hot_news_dict in data_dict:
        parsed_list.append(parse_hot_news_json_data(one_hot_news_dict))
    return parsed_list


def gener_hot_news_msg():
    parsed_list = parse_html(get_html())
    hot_news_head = "<h1>微博热搜</h1>"
    hot_news = ""
    count = 1
    for one_hot_news in parsed_list:
        if count == 11:
            break
        hot_news += "{}.<{}><a href='{}'>{}</a>".format(count,
                                                        one_hot_news["label"], one_hot_news["url"],
                                                        one_hot_news["title"])
        hot_news += '<br>'
        count += 1

    return hot_news_head + hot_news


def hot_news_job():
    try:
        return gener_hot_news_msg()
    except:
        return "hot_news_job_error"
