# -*- coding: utf-8 -*-
from urllib.request import urlopen, Request
import requests
import zlib
import re
import os
import time
import jieba
import jieba.analyse
from collections import Counter
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import imageio
#from scipy.misc import imread #scipy1.2版本弃用imread
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

#判断历史弹幕还是当前弹幕
def choice_check(choice, oid):
    if(choice == '2'):
        deadline = input("历史弹幕查询截止时间（格式示例：2019-01-13）：")
        url = get_history_url(oid, deadline)
        comment = get_history_comment(url)
    elif(choice == '1'):
        url = get_current_url(oid)
        comment = get_current_comment(url)
    else:
        print("ERROR")
    return comment

#拼接完整url
#当前弹幕池
def get_current_url(oid):
    url = 'http://comment.bilibili.com/' + oid + '.xml'
    #url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + oid
    #两种均可使用，但第一个可不登陆
    return url

#历史弹幕池
def get_history_url(oid, deadline):
    url = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid=' + oid + '&date=' + deadline
    return url

#从网页获取xml，并进行格式处理
def get_current_comment(url):
    #读取xml文件
    response = urlopen(Request(url, headers={'Accept-Encoding': 'identity,gzip,deflate;q=0'}))
    #终端中判断格式：deflate
    #response.info().get('Content-Encoding')

    #解压
    decompressed_data = zlib.decompress(response.read(), -zlib.MAX_WBITS)
    text = decompressed_data.decode('utf8').splitlines(True)[:10]

    #格式转换，正则获取，写入文件
    text_final = str(text)
    comment = re.findall(r'<d .*?>(.*?)</d>',text_final)
    return comment
    
def get_history_comment(url):
    headers={
	'Host': 'api.bilibili.com',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate, br, identity;q=0',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cookie': '_uuid=73615F5B-6D29-D432-5B4A-9C3F88DA02A662263infoc; buvid3=B50EB75D-24B1-4018-A670-88F26C669CB7155806infoc; LIVE_BUVID=AUTO1815686341658994; CURRENT_FNVAL=16; stardustvideo=1; sid=k1bjanqt; DedeUserID=11773002; DedeUserID__ckMd5=4c25b843892ce865; SESSDATA=b39dc2e4%2C1572258610%2Cc8bed491; bili_jct=25381bb83fe7796b1d4607edbc6f91d5'
		}

    try:
        #延时操作
        time.sleep(0.5)
        response=requests.get(url,headers=headers)
        response.encoding="utf-8" #编码
    except Exception as e:
        print('获取xml内容失败,%s' % e)

    else:
        if response.status_code == 200:
            text = response.text
            text_final = str(text)
            comment = re.findall(r'<d .*?>(.*?)</d>',text_final)
            
    return comment

#写入文件
def write_file(file_name,data): 
    i=1
    all_word_list = []
    file_path = os.getcwd() + '/' + file_name

    #判断文件是否已存在，若存在，则删除
    if os.path.exists(file_path):
        os.remove(file_path)

    #写入，采用循环，模式a+，附加写入
    font = open(file_name, 'a+', encoding='utf-8')
    for i in range(len(data)):
        #print(comment[i])
        all_word_list.append(data[i])   # 使用 append() 添加元素
        font.write(str(all_word_list[i]) + '\n')

    #关闭文件
    font.close()


#jieba计数
def jieba_counter(file_name):
    #调用自定义dic
    #jieba.load_userdict('user_dic.txt')
    
    #分词
    cut_words=""
    for line in open(file_name,encoding='utf-8'):
        line.strip('\n')
        #line = re.sub("[A-Za-z0-9\：\·\—\，\。\“ \”]", "", line)
        seg_list=jieba.cut(line,cut_all=False)
        cut_words+=(" ".join(seg_list))
    all_words=cut_words.split()
    
    #计数器
    c=Counter()
    for x in all_words:
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    write_file('wordCounter.txt',c.most_common())

#词云制作
def word_cloud(file_name, fontpath, background_pic):
    #打开文件进行分词
    text = open(file_name , 'r', encoding = 'utf-8').read()
    word_split = jieba.cut(text, cut_all = False)
    word_space = ' '.join(word_split)
    #print(word_space)
    
    #获取背景图
    background = background_pic
    img = imageio.imread(background)
    img = np.array(Image.open(background))
    #检测图是否导入
    '''
    plt.imshow(img)
    plt.axis('off')
    plt.show()
    '''
    
    #编写词云
    my_wordcloud = WordCloud(
        scale=6,
        width=1000,
        height=600,
        #min_font_size=20, #可选是否不要低于此size的词条
        background_color='white',
        mask=img,
        max_words=200,
        stopwords=STOPWORDS,
        font_path=fontpath,
        max_font_size=100,
        random_state=50,
        ).generate(word_space)
    image_color = ImageColorGenerator(img)
    
    #预览
    plt.imshow(my_wordcloud)
    plt.axis('off')
    plt.show()

    #存入
    my_wordcloud.to_file('res.jpg')

'''
例子
春决垃圾话：oid='87198325'
ig vs g2：oid='60824006'
ig vs fnc：oid='61680672'
'''

#url拼接
choice = input("请输入数字：1.查询当前弹幕；2.查询历史弹幕。")
oid = input("请输入视频oid：")
file_name = input("储存文件(txt文件)名？（格式示例：comment.txt）")

#评论获取并写入文件
comment = choice_check(choice, oid)
write_file(file_name,comment)

#分词计数写入文档
jieba_counter(file_name)

#词云制作
font_path = r'.\\Fonts\\FZLTXIHK.TTF'  #字体文件路径，可自定义
background_pic = 'ig.jpg'  #背景图路径，可自定义
word_cloud(file_name, font_path, background_pic)