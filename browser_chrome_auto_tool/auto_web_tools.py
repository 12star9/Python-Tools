#!/usr/bin/env python
# -*- coding: utf-8 -*-

from splinter.browser import Browser
import time
import re
import os

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


global_print_switch='cmd';

def g_print(str,state=True):
    returnResult=str;
    if global_print_switch==u'default':
        returnResult=str;
        if state==True:
            print str;
    elif global_print_switch==u'none':
        pass
    elif global_print_switch==u'cmd':
        returnResult=str.decode("utf-8").encode('gbk');
        if state == True:
            print returnResult;
    return returnResult;

def quit_browser(browser=None):
    flag = input(g_print(u'输入q来退出浏览器!',False))
    if 1 == int(flag):
        quit(browser)

def add_new_product_to_exist(browser,key_name):
    add_new_product = browser.find_by_xpath('/html/body/div[2]/div/div[2]/a').first;
    if add_new_product.value == u'+ 添加商品':
        add_new_product.click();
        g_print(u'正在添加.....,持续等待1秒.');
        time.sleep(1);
        # 会打开一个新窗口
        g_print( u'填充关键字!!')
        browser.find_by_id(u"searchInput").first.fill(key_name);
        g_print( u'开始搜索....')
        browser.find_by_id(u"search-btn").first.click();
        g_print( u'开始呈现搜索结果.....,持续等待5秒.')

        time.sleep(5);
        g_print( u'搜索结果呈现完成!!')

        while True:
            flag = input(g_print(u'请勾选你需要的商品后，按下1继续', False))
            if 1 == int(flag):
                break;
        add_to_basket = browser.find_by_xpath('/html/body/div[2]/div/div/div[1]').first;
        if add_to_basket.value == u'添加到商品包':
            add_to_basket.click();
            g_print( u'正在添加.....,持续等待2秒.')
            time.sleep(2);
            g_print( u'添加完成!!等到下一件商品添加.....')

def start(browser,product_name,product_des,keys):
    product_basket_name=product_name;
    product_basket_des = product_des;
    search_product_key_txt=keys[0];
    # chrome_driver='E:\Users\star\PycharmProjects\untitled\chromedriver_win32\chromedriver.exe'
    # browser=webdriver.Chrome(executable_path=chrome_driver)
    # browser.visit('http://neuhub.jd.com/user/baseInfo')
    # browser.visit('https://passport.jd.com/uc/login?ReturnUrl=http%3A%2F%2Fneuhub.jd.com%2Fuser%2FbaseInfo')
    browser.visit('http://kepler.jd.com/console/app/app_list.action')
    username='登入账号名'
    password='登入密码'

    browser.find_by_xpath('/html/body/div[2]/div[2]/div[1]/div/div[3]/a').first.click()
    browser.find_by_id(u"loginname").first.fill(username)
    browser.find_by_id(u"nloginpwd").first.fill(password)
    browser.find_by_id("loginsubmit").first.click()

    g_print( u'请在15秒内滑动滑块进行登录！！！！！！！！！！！！！！！！！！！！！')

    time.sleep(15)

    browser.visit('http://kepler.jd.com/console/app/app_list.action')

    g_print( u'完成登录了!')

    while(1):
        try:
            temp=browser.find_by_xpath('/html/body/div[2]/div[2]/div/table/tbody/tr[3]/td[1]/div[2]/a').first;
            if temp.value==u'****应用名':
                break
            continue
        except ZeroDivisionError,e:
            
            g_print(u'找不到****应用！')
            continue

        g_print( 'done')

    temp=browser.find_by_xpath('/html/body/div[2]/div[2]/div/table/tbody/tr[3]/td[1]/div[2]/a')
    temp.click()
    g_print( u'完成****的跳转了!')

    g_print( u'正在等待跳转后的网页呈现.....,持续等待4秒.')
    time.sleep(4)

    targetElement=browser.find_by_xpath('/html/body/div[2]/div[1]/div[2]/div[1]/div/ul[2]/li[2]/a').first;
    if targetElement.value==u'我的选品':
        targetElement.click();
        g_print( u'完成*****应用-我的选品页面的切换!')
        g_print( u'等待2秒.')
        time.sleep(2);
        with browser.get_iframe('flowDataiframeId') as iframe:
            # 这里要判断有没有老商品包
            tbody_element= browser.find_by_id('pkg-list-tbody').first;
            last_element = browser.find_by_xpath('/html/body/div[1]/div/table/tbody/tr[1]/td[3]/a').first;
            last_all_element=browser.find_by_css('.act-details');

            for temp_Element in last_all_element:
                if temp_Element.value == product_basket_name:
                    last_element=temp_Element;
                    break;
                else:
                    continue;
            if last_element.value == product_basket_name:
                g_print( u'已发现配置好的商品包.....,持续等待2秒.')
                g_print( u'跳转到该已经创建好的商品包的详情页面');
                time.sleep(2)
                stringTemp=last_element.outer_html;
                result = re.findall(r'/console/(.*)t=1', stringTemp)
                navigate_url = 'http://kepler.jd.com/console/' + result[0] + 't=1';
                navigate_url=navigate_url.replace('amp;','');
                browser.visit(navigate_url);
                g_print( u'进入商品包详情页面.....,持续等待1秒.')

                time.sleep(1);
                for key_name in keys:

                    add_new_product_to_exist(browser,key_name);

            else:
                create_new_Products=browser.find_by_id('create-pkg').first;
                if create_new_Products.value==u'+ 新建商品包':
                    g_print( u'开始新建商品包!')
                    create_new_Products.click();
                    g_print( u'等待页面呈现.....!')
                    time.sleep(3);
                    g_print( u'页面呈现完成!!')
                    g_print( u'填充关键字!!')
                    browser.find_by_id(u"searchInput").first.fill(search_product_key_txt);
                    g_print( u'开始搜索....')
                    browser.find_by_id(u"search-btn").first.click();
                    g_print( u'开始呈现搜索结果....')
                    time.sleep(3);
                    g_print(u'搜索结果呈现完成!!')
                    while True:

                        flag = input(g_print(u'请勾选你需要的商品后，按下1继续',False))
                        if 1== int(flag):
                            break;
                    create_basket=browser.find_by_xpath('/html/body/div[2]/div/div[1]').first;
                    if create_basket.value==u'创建商品包':
                        create_basket.click();
                        time.sleep(2);
                        product_name= browser.find_by_xpath('/html/body/div[4]/div[2]/div/div[2]/span[2]/input').first;
                        product_des=browser.find_by_xpath('/html/body/div[4]/div[2]/div/div[3]/span[2]/textarea').first;
                        product_name.fill(product_basket_name);
                        product_des.fill(product_basket_des);

                        imediateCreate= browser.find_by_xpath('/html/body/div[4]/div[2]/div/div[4]/span[1]').first;
                        if imediateCreate.value==u'立即创建':
                            imediateCreate.click();
                            g_print(u'开始创建商品包信息');
                            time.sleep(2);

                            look_products= browser.find_by_xpath('/html/body/div[4]/div/div/div[2]/span[1]/a').first;
                            if look_products.value==u'查看商品包':
                                look_products.click();
                                g_print(u'查看商品包列表数据');
                                # 最新创建的商品包排在最前面
                                new_element=browser.find_by_xpath('/html/body/div[1]/div/table/tbody/tr[1]/td[3]/a').first;
                                if new_element.value==product_basket_name:
                                    stringTemp = new_element.outer_html;
                                    result = re.findall(r'/console/(.*)t=1', stringTemp)
                                    navigate_url = 'http://kepler.jd.com/console/' + result[0] + 't=1';
                                    navigate_url = navigate_url.replace('amp;', '');
                                    browser.visit(navigate_url);
                                    time.sleep(1);
                                    for index in range(len(keys)):
                                        if index==0:
                                            continue;
                                        add_new_product_to_exist(browser,keys[index]);

def getProductsConfig():
    product_name='';
    product_des='';
    keys=[];
    for filename in os.listdir(r"./products"):  # listdir的参数是文件夹的路径
        filename=filename.decode('gbk');
        pathUrl = "./products/" + filename
        (filepath, tempfilename) = os.path.split(filename);
        tempResult=tempfilename.split('&&&');
        product_name=tempResult[0];
        product_des=tempResult[1].split('.txt')[0];

        if isinstance(product_name, unicode):
            pass
        else:
            product_name = unicode(product_name, 'utf-8')
        if isinstance(product_des, unicode):
            pass
        else:
            product_des = unicode(product_des, 'utf-8')


        for line in open(pathUrl):

            search_product_key = line.encode('utf-8');
            if isinstance(search_product_key, unicode):
                pass
            else:
                search_product_key = unicode(search_product_key, 'utf-8')
            keys.append(search_product_key);
    browser = Browser(driver_name='chrome')
    start(browser,product_name,product_des,keys);
    quit_browser(browser)

if __name__ == "__main__":
    getProductsConfig();
