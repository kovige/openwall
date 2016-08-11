# -*- coding:utf8 -*-
import re
import requests
import argparse
import sys
import threading
import time
import Queue
from pyh import *
import random

threads_num = 12
BROWSERS = (
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.6) Gecko/2009011912 Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.48 Safari/525.19',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.648)',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.5) Gecko/2008121621 Ubuntu/8.04 (hardy) Firefox/3.0.5',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-us) AppleWebKit/525.27.1 (KHTML, like Gecko) Version/3.2.1 Safari/525.27.1',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'
)
HEADER = {'user-agent': random.choice(BROWSERS)}
batch_url = []
batch_title = []

def get(url):
    r_url = r'<li><a href="(\d\d/\d+)">[^\n]*?</a> \(cve-assign&#64;...re.org\)'    
    reg_url = re.compile(r_url)
  
    try:
        res = requests.get(url,headers = HEADER,timeout = 5)
        html = res.text
    except Exception,e:
        print 'get html error'
        return None
    list_url = reg_url.findall(html)
    list_title = []
    for num in xrange(0,len(list_url)):
        r_title = r'<li><a href="%(url)s">([^\n]*?)</a> \(cve-assign&#64;...re.org\)' % {'url': list_url[num]}
        reg_title = re.compile(r_title)
        title = reg_title.findall(html)
        list_title.append(title[0])
        list_url[num] = url+list_url[num]
    return list_title,list_url
    

def get_batch():
    while True:
        if queue.empty():
            break
        one_url = queue.get_nowait()
        print one_url
        (list_title,list_url) = get(one_url)
        for url in list_url:
            batch_url.append(url)
        for title in list_title:
            batch_title.append(title)
            
    

def to_html(list_url,list_title):
    page = PyH('Results '+year+' '+month)
    page.addCSS('style.css')
    div_1 = page << div(cl='help',id='table')
    div_2 = div_1 << h1('Exploit Table:')
    table_1 = div_1 << div(cl='col w10 last') << div(cl = 'content') << table()
    table_1 << tr(th('Url')+th('Title'))
    for num in xrange(0,len(list_url)):
        one_url = list_url[num]
        tr_1 = table_1 << tr(id = 'id_1')
        tr_1 << td() << a(list_url[num],href=one_url)
        tr_1 << td(list_title[num])
    
    fileName = str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())))+'_'+year+month+'.html'
    page.printOut(fileName, 'utf-8')


def run(url):
    month_num = 12
    local_year = time.strftime('%Y',time.localtime(time.time()))
    local_month = time.strftime('%m',time.localtime(time.time()))
    if(year == local_year):
        month_num = 0
        for num in xrange(0,int(local_month)):
            month_num = month_num+1
    for num in xrange(1,month_num+1):
        if num < 10:
            num = '0'+str(num)
        one_url = url+'/'+str(num)+'/'
        queue.put(one_url)
    
    threads = []
    for i in range(threads_num):
        t = threading.Thread(target=get_batch,name=str(i))
        threads.append(t)
  
    for t in threads:
        t.start()  
  
    t.join()
    time.sleep(threads_num)
    
def parse_args():
    parser = argparse.ArgumentParser(description="find new cves")
    parser.add_argument('--year', metavar='year', type=str, default='', help='year like 2016')
    parser.add_argument('--month', metavar='month', type=str, default='', help='month like 01')
    if len(sys.argv) < 1:
        sys.argv.append('-h')
    args = parser.parse_args()
    return args  

def check(args): 
    global year 
    year = args.year
    global month
    month = args.month
    local_year = time.strftime('%Y',time.localtime(time.time()))
    local_month = time.strftime('%m',time.localtime(time.time()))
    if year == '':
        msg = 'must input a year'
        raise Exception(msg)
    if not year.isdigit():
        msg = 'input must be integer'
        raise Exception(msg)
    if int(year)>int(local_year):
        msg = 'invalid year'
        raise Exception(msg)
    while(year.startswith('0') is True):
        year = year[1:]
    if int(year)<2009:
        msg = 'nothing before 2009'
        raise Exception(msg)
        
    if month:
        if not month.isdigit():
            msg = 'input must be integer'
            raise Exception(msg)    
        if int(month)>13 or int(month)<1:
            msg = 'invalid month'
            raise Exception(msg)
        if year == local_year:
            if int(month)>int(local_month):
                msg = 'invalid month'
                raise Exception(msg)    
        while(month.startswith('0') is True):
            month = month[1:]
        if int(month)<10:
            month = '0'+month
        url = 'http://www.openwall.com/lists/oss-security/'+year+'/'+month+'/'
    else:
        url = 'http://www.openwall.com/lists/oss-security/'+year
    return url

if __name__ == '__main__':
    args = parse_args()
    url = check(args)
    print url
    if url.endswith('/'):
        (list_title,list_url) = get(url)
        to_html(list_url,list_title)
        print 'finished...'
    else:
        global queue
        queue = Queue.Queue()
        run(url)
#         print len(batch_url)
#         print len(batch_title)
        to_html(batch_url,batch_title)    
        print 'finished...'

    