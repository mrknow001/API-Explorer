# -*- coding: utf-8 -*-
"""
@Time ： 2023/7/4 10:37
@Auth ： YD
@File ：ParamsAnalysis.py
@IDE ：PyCharm
@Description ：参数解析
"""
import json

import requests
import re
from urllib.parse import parse_qs

# 忽略https证书
requests.packages.urllib3.disable_warnings()

# 代理
proxies = {"http":"http://127.0.0.1:8080","https":"http://127.0.0.1:8080"}

# 将参数解析成列表
def get_list_params(get_params, headers, post_params):
    if get_params != '':
        get_params_dict = parse_qs(get_params, keep_blank_values=True)
        get_result = [["get."+key, value[0]] for key, value in get_params_dict.items()]
    if headers != '':
        headers_dict = parse_qs(headers, keep_blank_values=True)
        headers_result = [["header."+key, value[0]] for key, value in headers_dict.items()]
    if post_params != '':
        post_params_dict = parse_qs(post_params, keep_blank_values=True)
        post_result = [["post."+key, value[0]] for key, value in post_params_dict.items()]

    # 合并列表
    if get_params != '' and headers != '' and post_params != '':
        result = get_result + headers_result + post_result
    elif get_params != '' and headers != '':
        result = get_result + headers_result
    elif get_params != '' and post_params != '':
        result = get_result + post_result
    elif headers != '' and post_params != '':
        result = headers_result + post_result
    elif get_params != '':
        result = get_result
    elif headers != '':
        result = headers_result
    elif post_params != '':
        result = post_result
    else:
        result = None
    return result

    # 修改参数
def change_params(old_params, new_params):
    # 将原参数get_params、headers、post_params取出解析成字典，并且将值的第0位取出
    old_params_dict = get_list_params(old_params.get_params,old_params.headers,old_params.post_params)
    # 将原get_list_params函数返回的列表转换成字典
    old_params_dict = dict(old_params_dict)
    # 新参数替换旧参数，遇到{id},{secert},{token}则跳过
    for key, value in old_params_dict.items():
        if value == "{id}" or value == "{secert}" or value == "{token}":
            new_params[key] = value
        else:
            continue
    # 将字典根据键的.前面区分成get、header、post三个字典
    get_params_dict = {key.split('.')[1]:value for key, value in new_params.items() if key.split('.')[0] == 'get'}
    headers_dict = {key.split('.')[1]:value for key, value in new_params.items() if key.split('.')[0] == 'header'}
    post_params_dict = {key.split('.')[1]:value for key, value in new_params.items() if key.split('.')[0] == 'post'}
    # 将字典转换成字符串
    get_params = '&'.join([key + '=' + value for key, value in get_params_dict.items()])
    headers = '&'.join([key + '=' + value for key, value in headers_dict.items()])
    post_params = '&'.join([key + '=' + value for key, value in post_params_dict.items()])

    return get_params, headers, post_params

# jssn嵌套字符串格式的json处理
def parse_json_values(data):
    for key, value in data.items():
        if isinstance(value, str):
            try:
                data[key] = json.loads(value)
            except json.JSONDecodeError:
                pass
        elif isinstance(value, dict):
            parse_json_values(value)
    return data

# 请求API
def get_api(params_info, ui_params, get_token=0):
    # 读取数据库中headers,并转换为字典
    headers = params_info.headers
    headers_dict = parse_qs(headers)
    # 值等于值的第0位
    headers_dict = {key:value[0] for key, value in headers_dict.items()}
    # 判断请求方法为get还是post,不区分大小写
    if params_info.type.upper() == 'GET':
        # 从数据库获取请求参数以及url后拼接，使用requests发送请求
        url = params_info.url
        params = params_info.get_params
        # 使用parse_qs将参数解析，并且替换特殊标识符，{id}替换为ui_params['id']，{key}替换为ui_params['key']，{token}替换为ui_params['token']
        params = parse_qs(params)
        #
        # 需要修改bug，如果字段中存在特殊标识符又存在普通字符，现在还没法完美修改
        #
        for key, value in params.items():
            if value[0] == '{id}':
                params[key] = ui_params['id']
            elif value[0] == '{secert}':
                params[key] = ui_params['key']
            elif value[0] == '{token}':
                params[key] = ui_params['token']
            else:
                params[key] = value[0]
        # 将参数与url拼接成requests可以使用的格式
        url = url + '?' + '&'.join([key + '=' + value for key, value in params.items()])
        try:
            # 请求时指定Accept为application/json
            headers_dict['Accept'] = 'application/json'
            # 发送请求
            response = requests.get(url, verify=False, headers=headers_dict, timeout=5)
            # 根据响应判断数据是否为json
            if 'application/json' in response.headers['Content-Type']:
                r_data = response.json()
            else:
                # 尝试将响应转换为json，如果失败则返回text
                try:
                    r_data = json.loads(response.content.decode('utf-8'))
                except:
                    r_data = response.content.decode('utf-8')
            # 判断是否获取token，如果是则提取token
            if get_token == 1:
                # 提取token，正则表达式从数据库获取
                token = re.findall(params_info.token_re, response.text)
                # 根据token长度判断是否获取到token
                if len(token) == 0:
                    return {"result":r_data, "token":"未获取到token"}
                else:
                    return {"result":r_data, "token":token[0]}
            # 如果不是获取token，返回{"result":response.text, "token":null}
            else:
                return {"result":r_data, "token":None}
        except Exception as e:
            return {"result":"获取失败，错误信息如下：\n"+str(e), "token":None}

    elif params_info.type.upper() == 'POST':
        url = params_info.url
        get_params = params_info.get_params
        headers = params_info.headers
        content_type = params_info.content_type
        post_params = params_info.post_params
        # 使用parse_qs将参数解析get_params、headers、post_params，并且替换特殊标识符，{id}替换为ui_params['id']，{key}替换为ui_params['key']，{token}替换为ui_params['token']
        # 处理get_params
        get_params = parse_qs(get_params)
        for key, value in get_params.items():
            if value[0] == '{id}':
                get_params[key] = ui_params['id']
            elif value[0] == '{secert}':
                get_params[key] = ui_params['key']
            elif value[0] == '{token}':
                get_params[key] = ui_params['token']
            else:
                get_params[key] = value[0]
        # get参数拼接url
        url = url + '?' + '&'.join([key + '=' + value for key, value in get_params.items()])
        # 处理headers
        headers = parse_qs(headers)
        for key, value in headers.items():
            if value[0] == '{id}':
                headers[key] = ui_params['id']
            elif value[0] == '{secert}':
                headers[key] = ui_params['key']
            elif value[0] == '{token}':
                headers[key] = ui_params['token']
            else:
                headers[key] = value[0]
        # 处理post_params
        post_params = parse_qs(post_params)
        for key, value in post_params.items():
            if value[0] == '{id}':
                post_params[key] = ui_params['id']
            elif value[0] == '{secert}':
                post_params[key] = ui_params['key']
            elif value[0] == '{token}':
                post_params[key] = ui_params['token']
            else:
                post_params[key] = value[0]
        # 将content_type追加到headers中
        headers['Content-Type'] = params_info.content_type
        try:
            # 请求时指定Accept为application/json
            headers['Accept'] = 'application/json'
            # 发送请求,判断content_type类型，如果是json，使用json参数发送请求，如果是form，使用data参数发送请求
            if content_type == 'application/json':
                # 将所有参数转换为json格式
                post_params = parse_json_values(post_params)
                response = requests.post(url, verify=False, headers=headers, json=post_params, timeout=5)
            elif content_type == 'application/x-www-form-urlencoded':
                response = requests.post(url, verify=False, headers=headers, data=post_params, timeout=5)
            else:
                return {"result": "暂不支持from、json以外参数类型", "token": None}
            # 根据响应判断数据是否为json
            if 'application/json' in response.headers['Content-Type']:
                r_data = response.json()
            else:
                # 尝试将响应转换为json，如果失败则返回text
                try:
                    r_data = json.loads(response.content.decode('utf-8'))
                except:
                    r_data = response.content.decode('utf-8')
            # 判断是否获取token，如果是则提取token
            if get_token == 1:
                # 提取token，正则表达式从数据库获取
                token = re.findall(params_info.token_re, r_data)
                # 根据token长度判断是否获取到token
                if len(token) == 0:
                    return {"result":r_data, "token":"未获取到token"}
                else:
                    return {"result":r_data, "token":token[0]}
            # 如果不是获取token，返回{"result":response.text, "token":null}
            else:
                return {"result":r_data, "token":None}
        except Exception as e:
            return {"result":"获取失败，错误信息如下：\n"+str(e), "token":None}
    else:
        return {"result":"暂不支持GET、POST以外方法", "token":None}