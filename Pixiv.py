#! /usr/bin/env python3
# -*- coding:utf-8 -*-
'''
Created on 2016年6月3日

@author: sugar
'''


import urllib.request
import re
import sys
import urllib.error
import urllib.parse
import http.cookiejar
import time
import socket
socket.setdefaulttimeout(60)


class GetPixiv():
    
    def __init__(self):
        #设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie 
        cj = http.cookiejar.LWPCookieJar()  
        cookie_support = urllib.request.HTTPCookieProcessor(cj)  
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)  
        urllib.request.install_opener(opener)
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36'}
        self.index_url = 'http://www.pixiv.net/' 
        self.login_getpostkey_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.main()
        
    def main(self):
        if self.login():
            print('登陆成功')
            # i = 1
            # while i < 57261500:
            #     self.get_images(i)
            #     i += 1
            i = 1
            while True:
                try:
                    self.ref_url = self.get_html_data(i)
                    print(self.ref_url)
                    # print(self.judge_type(i))
                    judge_type = self.judge_type(i)
                    print(judge_type)
                    score_count = self.judge_score_count()
                    print(score_count)
                    if judge_type:
                        print('manga')
                    elif score_count:
                        px = self.judge_px()
                        print(px)
                        r18 = self.judge_r18()
                        print(r18)
                        self.get_image_name_extension()
                        self.judge_dir(score_count,px,r18,i)
                    else:
                        pass
                except urllib.error.URLError as e:
                    if hasattr(e,'reason'):
                        print(e.reason)
                    if hasattr(e,'code'):
                        print(e.code)
                except:
                    print('timeout')
                i += 1
                print(i)
                # if i % 100 == 0:
                #     print('sleep')
                #     time.sleep(3)
        else:
            print('登陆失败，请重新运行程序')


    def login(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36',
                'Host':'accounts.pixiv.net',
                'Origin':'https://accounts.pixiv.net',
                'Referer':'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'}
        try:
            urllib.request.urlopen(self.index_url)
            postkey_html = urllib.request.urlopen(self.login_getpostkey_url).read().decode('utf-8')
            pattern = re.compile(r'post_key".*?"(.*?)"')
            post_key = re.findall(pattern, postkey_html)
            post_data2 = urllib.parse.urlencode({'pixiv_id':'lu973076977@qq.com',
                                                'password':'lu19930913',
                                                'captcha':'',
                                                'g_recaptcha_response':'',
                                                'post_key':'%s' %(post_key[0]),
                                                'source':'pc'}).encode('utf-8')
            req = urllib.request.Request(self.login_url,post_data2,headers=headers)
            res = urllib.request.urlopen(req)
        except urllib.error.URLError as e:
            if hasattr(e,'reason'):
                print(e.reason)
            if hasattr(e,'code'):
                print(e.code)
            return False
        return True

    def get_html_data(self,illustid):
        url = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id=%d' %(illustid)
        self.res_html = urllib.request.urlopen(url).read().decode('utf-8')
        return url

    def judge_type(self,illustid):
        try:
            pattern = re.compile(r'works_display.*?member_illust\.php\?mode=manga.*?id=(.*?)"')
            result = re.findall(pattern,self.res_html)
            if int(result[0]) == illustid:
                url = 'http://www.pixiv.net/member_illust.php?mode=manga&illust_id=%d' %(illustid)
                return url
            else:
                return False
        except IndexError as e:
            print(e)
            return False

    def judge_r18(self):
        try:
            pattern = re.compile(r'<li class="r-18">R-18</li>')
            result = re.findall(pattern,self.res_html)
            if result:
                return 'R18'
            else:
                return False
        except:
            return False

    def judge_score_count(self):
        try:
            original_image_pattern = re.compile(r'data-src="(.*?)".*?class="original-image"')
            images_url = re.findall(original_image_pattern,self.res_html)
            self.images_url = images_url[0]
            if images_url is None:
                # print('这里木有图，到下一个去了。')
                return False
            else:
                # print('这里有图，我来看看评分和分辨率')
                score_count_pattern = re.compile(r'"score-count">(.*?)</dd>')
                self.score_count = int(re.findall(score_count_pattern,self.res_html)[0])
                if self.score_count > 50000:
                    # print('这图评分:%d分，我收了' %self.score_count)
                    px_pattern = re.compile(r'<li>(\d+)×(\d+)</li>')
                    px = re.findall(px_pattern,self.res_html)
                    # print(px)
                    # print(type(px))
                    # print(px[0][0],px[0][1])
                    # print(type(px[0][0]))
                    self.px_w = int(px[0][0])
                    self.px_h = int(px[0][1])
                    # print('图的分辨率为%d*%d' %(self.px_w, self.px_h))
                    return '5Wscore'
                elif self.score_count < 5000:
                    # print('评分小于1000，这图我不要')
                    return False
                else:
                    px_pattern = re.compile(r'<li>(\d+)×(\d+)</li>')
                    px = re.findall(px_pattern,self.res_html)
                    # print(px)
                    # print(type(px))
                    # print(px[0][0],px[0][1])
                    # print(type(px[0][0]))
                    self.px_w = int(px[0][0])
                    self.px_h = int(px[0][1])
                    # print('图的分辨率为%d*%d' %(self.px_w, self.px_h))
                    return '5K-5Wscore'
        except IndexError as e:
                # print('这里没有图片')
                return 'SB'

    def judge_px(self):
        if self.px_w > 1920 and self.px_h > 1080:
            return 'wallpaper'
        elif self.px_w > 800 and self.px_h > 800:
            return 'MyHarem'
        else:
            return 'other'

    def get_image_name_extension(self):
        try:
            image_name_pattern = re.compile(r'ul><h1 class="title">(.*?)</h1>')
            image_name_data = re.findall(image_name_pattern,self.res_html)
            self.image_name = image_name_data[0]
            self.image_extension = self.images_url.split('.')[-1]
        except IndexError as e:
            print(e)



    def get_images_data(self):
        for i in range(5):
            try:
                print('this is get_images_data')
                images_req = urllib.request.Request(self.images_url,headers=self.headers)
                images_req.add_header('Referer',self.ref_url)
                images_data = urllib.request.urlopen(images_req).read()
                print('it\'s over')
                return images_data
            except urllib.error.URLError as e:
                if hasattr(e,'reason'):
                    print(e.reason)
                if hasattr(e,'code'):
                    print(e.code)
        return False

    def judge_dir(self,score_count,px,r18,i):
        if r18 == 'R18':
                px = 'R18'
                images_data = self.get_images_data()
                if images_data:
                    self.download_images(images_data,px,i)
        elif score_count == '5Wscore':
            if px == 'wallpaper':
                images_data = self.get_images_data()
                if images_data:
                    self.download_images(images_data,'5Wscore/'+px,i)
            elif px == 'MyHarem':
                images_data = self.get_images_data()
                if images_data:
                    self.download_images(images_data,'5Wscore/'+px,i)
            else:
                images_data = self.get_images_data()
                if images_data:
                    self.download_images(images_data,'5Wscore/'+px,i)
        elif score_count == '5K-5Wscore':
            if px == 'wallpaper':
                images_data = self.get_images_data()
                if images_data:
                    self.download_images(images_data,px,i)
            elif px == 'MyHarem':
                images_data = self.get_images_data()
                if images_data:
                    self.download_images(images_data,px,i)
            else:
                pass
        else:
            pass


    def download_images(self,images_data,px,i):
        dir = '/pixiv/%s/%s.%s' %(px,str(i)+'&'+str(self.image_name)+'&'+str(self.score_count),str(self.image_extension))
        with open(dir,'wb') as f:
            f.write(images_data)
        print('成功录入在%s' %(dir))
    def get_manga(self,url):
        '''以后想要再爬'''
        pass


a = GetPixiv()

