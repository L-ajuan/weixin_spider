import requests
import json
from requests.packages import urllib3
import re
import time
urllib3.disable_warnings()

class WeixinSpider(object):
    def __init__(self, url, cookie):
        '''
        初始化参数, 微信公众号cookie 和 url变得特别快，需要经常抓包获得
        '''
        self.s = requests.session()
        self.url = url
        self.appmsg_token = re.findall(r'appmsg_token=(.*?)&x5=0', self.url)[0]
        self.cookie = cookie
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1295.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.5 WindowsWechat',
            'Cookie': cookie,
        }

    def get_page(self):
        try:
            resp = self.s.get(self.url)
            if resp.status_code == 200:
                res = resp.json()
                if 'general_msg_list' not in res.keys():
                    raise Exception('url和cookie错误，请更新')
                article_list = self.get_article_msg(res)
                return article_list
        except Exception as f:
            print(f)



    def get_read_num(self, article_url):
        '''
        获取文章阅读数和点赞数
        '''
        __biz = re.findall(r'__biz=(.*?)&', article_url)[0]
        mid = re.findall(r'mid=(\d+)&', article_url)[0]
        idx = re.findall(r'idx=(\d+)&', article_url)[0]
        sn = re.findall(r'sn=(.*?)&', article_url)[0]
        origin_url = "https://mp.weixin.qq.com/mp/getappmsgext?"
        appmsgext_url = origin_url + "__biz={}&mid={}&sn={}&idx={}&appmsg_token={}&x5=1".format(__biz, mid, sn, idx,self.appmsg_token)

        data = {
            'is_only_read': '1',
            'is_temp_url': '0',
            'appmsg_type': '9',
        }
        content = requests.post(appmsgext_url, headers=self.headers, data=data, verify=False).json()
        if 'appmsgstat' not in content.keys():
            raise Exception('信息错误，请检查cookie和appmsg_token')
        try:
            appmsgstat = content['appmsgstat']
            read_num = appmsgstat['read_num']
            like_num = appmsgstat['like_num']
            # print(read_num)
            # print(like_num)
            return read_num, like_num
        except Exception:
            raise Exception('参数错误，请检查文章url')

    def get_article_msg(self, res):
        articles_list = []
        # 定义每日公众号字典
        data_list = res['general_msg_list']
        print(data_list)
        msg_list = eval(data_list)
        for msg in msg_list['list']:
            # 公众号每条文章信息
            article_dict = {}
            date_time = msg['comm_msg_info']['datetime'] #发布时间
            date_time = time.strftime("%Y-%m-%d %X", time.localtime(date_time))
            article_dict['postdate'] = date_time
            app_msg_ext_info = msg['app_msg_ext_info']
            first_title = app_msg_ext_info['title']    #标题
            # print(first_title)
            article_dict['article_title'] = first_title
            first_digest = app_msg_ext_info['digest'] #摘要
            # print(first_digest)
            article_dict['article_digest'] = first_digest
            first_url = app_msg_ext_info['content_url'] #文章链接
            # print(first_url)
            article_dict['article_url'] = first_url
            firsy_read_num, first_like_num = self.get_read_num(first_url)
            # print(firsy_read_num, first_like_num)
            article_dict['article_read_num'] = firsy_read_num
            article_dict['article_like_num'] = first_like_num
            first_imgurl = app_msg_ext_info['cover']
            # print(first_imgurl)
            article_dict['article_imgurl'] = first_imgurl
            first_author = app_msg_ext_info['author']
            # print(first_author)
            article_dict['article_author'] = first_author
            print(article_dict)
            article_msg = json.dumps(article_dict)
            with open('weixin_data.txt', 'a+', encoding='utf-8') as f:
                f.write(article_msg + '\n')
                f.close()
            articles_list.append(article_dict)
            for remain_msg in app_msg_ext_info['multi_app_msg_item_list']:
                second_title = remain_msg['title']
                # print(second_title)
                article_dict['article_title'] = second_title
                second_digest = remain_msg['digest']
                # print(second_digest)
                article_dict['article_digest'] = second_digest
                second_url = remain_msg['content_url']
                # print(second_url)
                article_dict['article_url'] = second_url
                second_read_num, second_like_num = self.get_read_num(second_url)
                # print(second_read_num, second_like_num)
                article_dict['article_read_num'] = second_read_num
                article_dict['article_like_num'] = second_like_num
                second_imgurl = remain_msg['cover']
                # print(second_imgurl)
                article_dict['article_imgurl'] = second_imgurl
                second_author = remain_msg['author']
                # print(second_author)
                article_dict['article_author'] = second_author
                print(article_dict)
                article_msg = json.dumps(article_dict)
                with open('weixin_data.txt', 'a+', encoding='utf-8') as f:
                    f.write(article_msg + '\n')
                    f.close()
                articles_list.append(article_dict)
            time.sleep(1)
        return articles_list

if __name__ == '__main__':
    url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzA4MTQ2NDg1NQ==&f=json&offset=0&count=10&is_ok=1&scene=124&uin=MTY4NzY0MTcwMw%3D%3D&key=1c83b2c1d811615e75ec4c21fa98677325dbf88d327baf84a3c926f3e769de0908dbbaa8441ea08d6947cdc4714a653275a0f8eb8765e3af046b5e3b37b627e041d85f266d6cb14819954b1e95c7571e&pass_ticket=Pb4wFxRa14W8NoOPWf900AyzBR8AerLpQDkhWEI5RUvWVR6MuhRFBNrkLDcz9Nwx&wxtoken=&appmsg_token=1051_rPXZxtAUYQpU6nDXnrJOueaaYqFV7CWKzGZ6Vg~~&x5=0&f=json'
    cookie = 'wxuin=1687641703; devicetype=iPhoneiOS13.3.1; version=17000b23; lang=zh_CN; pass_ticket=Pb4wFxRa14W8NoOPWf900AyzBR8AerLpQDkhWEI5RUvWVR6MuhRFBNrkLDcz9Nwx; wap_sid2=COe83aQGElxaVmtmWDhaSkw3SEtUSURpZTBiRGhUUnhCeF8xUWx6N3JnLWk2NXdGTU9sRTRGRWFYc1pJbkZNa1U1R29GMVZ4di1VYld4VWgxZkQ1NlFna2tTTUFieHNFQUFBfjD52o7zBTgNQJVO'
    spider = WeixinSpider(url, cookie)
    article_list = spider.get_page()
    print(article_list)




