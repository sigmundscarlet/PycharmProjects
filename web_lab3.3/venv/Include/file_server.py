import asyncio
import os
import mimetypes
import urllib
send_html = [b'HTTP/1.0 200 OK\r\n',#响应目录
            b'Connection: close',
            b'Content-Type:text/html; charset=utf-8\r\n',
            b'\r\n'
            ]
send_file = [b'HTTP/1.0 200 OK\r\n',#响应文件
             b'Connection: close',
             'Content-Type:{}\r\n',
             'Content-Length:{}\r\n',
             b'\r\n'
             ]
error_404 = [b'HTTP/1.0 404 Not Found\r\n',
             b'Connection: close',
             b'Content-Type:text/html; charset=utf-8\r\n',
             b'\r\n',
             b'<html><body>404 Not Found<body></html>',
             b'\r\n'
            ]
error_405=[b'HTTP/1.0 405 Method Not Allowed\r\n',
           b'Connection: close',
           b'Content-Type:text/html; charset=utf-8\r\n',
           b'\r\n',
           b'<html><body>405 Method Not Allowed<body></html>',
           b'\r\n'
           ]

html_background='<html><head><meta charset="utf-8" ><title>{}/</title></head> <body bgcolor="white"> <h1>{}/</h1><hr> <pre> {} </pre> <hr> </body></html> '#网页整体布局
file_button ='<a href="{}" download="{}">{}</a><br> '#需要下载的文件按钮
html_button ='<a href="{}" >{}</a><br>'#需要打开的文件按钮包括目录
def open_file(path):#打开处理文件
    file_type=list(mimetypes.guess_type(path))
    istxt=False
    if file_type[0] is None:#如果文件类型不可识别
        file_type[0] = 'application/octet-stream'
        file = open(path, 'rb')
    elif file_type[0][0:4]=='text':#是否是文本
        file = open(path,encoding='utf8')
        istxt=True
    else:
        file = open(path, 'rb')
    #print(file_type[0])
    file_size=os.path.getsize(path)#获取文件大小
    return ['file',file,file_type[0],file_size,istxt]
def creat_html(path):#产生目录下的页面
          file_list=os.listdir(path)
          button_adder=''
          if path != './':
              father_path=os.path.dirname(os.path.dirname(path))#获得父目录路径
              #print(father_path)
              button_adder=html_button.format(father_path[1:]+'/',"../")
          for file_obj in file_list:
              #print(file_obj)
              temp_path=path+file_obj#获得当前obj的路径
              #print(temp_path)
              file_type=mimetypes.guess_type(temp_path)[0]#获得当前obj类型
             # if  file_type is not None:
               # print(file_type[0:5])
              if os.path.isdir(temp_path) :#如果是目录
                  temp_path+='/'
                  file_obj+='/'
                  button_adder += html_button.format(temp_path[1:], file_obj)#使用打开按钮
              elif file_type is not None and file_type[0:4] == 'text':#如果是文本
                  #print(file_type[0:5])
                  button_adder += html_button.format(temp_path[1:], file_obj)#使用打开按钮
              else:
                  button_adder += file_button.format(temp_path[1:],file_obj, file_obj)#使用下载按钮
          return ["dir",html_background.format(path,path,button_adder)]

def get_url(req):
    url_list=urllib.parse.unquote(req.decode()).split(' ')
    #print(url_list)
    head_op=True #判断是否是head方法
    if url_list[0]=='POST':
        return ['error_405']
    elif url_list[0]=='GET':
        head_op=False
    path='.'+url_list[1]
    if os.path.exists(path):
        try:
            if os.path.isfile(path):
                return open_file(path)+[head_op]
            else:
                return creat_html(path)+[head_op]
        except FileNotFoundError:#找不到文件
            return ['error_404']
    else:#如果路径不存在
        return  ['error_404']

async def dispatch(reader,writer):
    local_judge=True
    while True:
        data = await reader.readline()
        if local_judge:#只解析第一行
           try:
                op_code=get_url(data)
                #print(data)
           except IndexError:
               op_code=['error_405']

        local_judge=False
        if data == b'\r\n':
            break
    if op_code[0]=='error_404':
        writer.writelines(
            error_404
        )
    elif op_code[0]=='error_405':
        writer.writelines(
            error_405
        )
    elif op_code[0]=='dir':
        if(op_code[2]):            #如果是head方法
            writer.writelines(
            send_html
            )
        else:
            writer.writelines(
                send_html+[op_code[1].encode('utf8')]+[b'\r\n']
        )
    else :
        if (op_code[5]):   #如果是head方法
            #print("1")
            writer.writelines(
            send_file[0:2]+[send_file[2].format(op_code[2]).encode('utf8')]+[send_file[3].format(op_code[3]).encode('utf8')]+[b'\r\n']
            )
        elif op_code[4]:#如果是文本
            #print("2")
            writer.writelines(
                send_file[0:2] + [send_file[2].format(op_code[2]).encode('utf8')] + [send_file[3].format(op_code[3]).encode('utf8')] + [b'\r\n'] + [('<xmp>'+op_code[1].read()+'</'+'xmp>').encode("utf8")] + [b'\r\n']
            )
        else:
            #print("3")
            writer.writelines(
                send_file[0:2] + [send_file[2].format(op_code[2]).encode('utf8')] + [send_file[3].format(op_code[3]).encode('utf8')] + [b'\r\n']+[op_code[1].read()]+[b'\r\n']
            )

        #print(send_file[0:2] + [send_file[2].format(op_code[2]).encode('utf8')] + [send_file[3].format(op_code[3]).encode('utf8')] + [b'\r\n']+[op_code[1].read()]+[b'\r\n'])
    await writer.drain()
    writer.close()

if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch,'127.0.0.1',8080,loop=loop)
    server = loop.run_until_complete(coro)

    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_close())
    loop.close