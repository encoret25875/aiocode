#!/usr/bin/python
# -*- coding: utf-8 -*-

from aiohttp import web
import aiohttp
import asyncio
import json
import requests
import time

# 基本api
async def handle(request):
    response_obj = {"status" :"success"}
    return web.Response(text=json.dumps(response_obj, status=200))

# 基本api(帶參數)
async def new_user(request):
    try:
        user = request.query['name']
        print("user name: ",user)

        response_obj = {'status': 'success', 'message': 'user successfull created'}
        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        response_obj = {'status': 'failed', 'message': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)

# -------------------------------------------------
# 非同步版本(使用到的func)
async def get_pk_info(session,id):
    pk_url = 'https://pokeapi.co/api/v2/pokemon/'
    async with session.get(pk_url + str(id))  as resp:
        pk_info = await resp.json()
        # print(str(id) + 'fin.')
        return "%d : %s" % (id, pk_info['name'])

# 非同步版本
# 先建立task list之後執行程式並等待所有task執行完成後繼續執行接下來程式
# gather好處在於將包起來一次處理開始或是await等動作
# await 等待指定的1或多個任務執行完成後繼續執行後續程式
# create_task 執行異步任務 有遇到await指定才會等待執行完成
async def searchpk_task(request):
    for i in range(1,10000000):
        i = i+1
    start = request.query['start']
    end   = request.query['end']
    # 需要大量 HTTP 要求
    async with aiohttp.ClientSession() as session:
        # create task list 
        # Wrap the coro coroutine into a Task and schedule its execution.
        tasks = []
        for id in range(int(start), int(end)+1):
            tasks.append(asyncio.create_task(get_pk_info(session, id)))
        # 執行task 
        all_info = await asyncio.gather(*tasks)

        # for info in all_info:
        #    print(info)
        response_obj = {'status': 'success', 'message': all_info}
    return web.Response(text=json.dumps(response_obj), status=200)


# 同步版本
#使用requests打別人api回傳資訊
def searchpk(request):
    start = request.query['start']
    end   = request.query['end']
    all_info = []
    
    for id in range(int(start), int(end)+1):
        resp = requests.get('https://pokeapi.co/api/v2/pokemon/' + str(id))
        pk_info = resp.json()
        all_info.append(str(id) + ' : ' + pk_info['name'])
    response_obj = {'status': 'success', 'message': all_info}
    return web.Response(text=json.dumps(response_obj), status=200)    

# 異步同步比較
# 動用異步func時須掛await不然func會直接死掉且會繼續執行
# 使用create_task會執行func且後面程式會繼續不會等待
async def searchpk_Compare(request):
    #start_time = time.time()
    #searchpk(request)
    #searchpk_time = time.time() - start_time
    
    start_time = time.time()
    await searchpk_task(request)
    searchpk_task_time = time.time() - start_time
    
    start_time = time.time()
    task1 = asyncio.create_task(searchpk_task(request))
    await task1
    create_task_time = time.time() - start_time

    #print('searchpk花費時間:   ' + str(searchpk_time))
    print('searchpk_task花費時間:   ' + str(searchpk_task_time))
    print('create_task花費時間:   ' + str(create_task_time))
    output = []
    #output.append('searchpk_time : ' + str(searchpk_time))
    output.append('searchpk_task_time : ' + str(searchpk_task_time))
    #output.append('Compare : ' + str(searchpk_time/searchpk_task_time))
    output.append('create_task_time : ' + str(create_task_time))
    return web.Response(text=json.dumps(output), status=200)

# --------------------------------------------------
app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/user', new_user)

# 異步使用
app.router.add_post('/searchpk_task', searchpk_task)
# 同步使用
app.router.add_post('/searchpk', searchpk)
# 比較使用
app.router.add_post('/searchpk_Compare', searchpk_Compare)


web.run_app(app)
