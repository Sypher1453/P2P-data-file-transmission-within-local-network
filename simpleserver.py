import http.server
import socketserver
import sys
import threading
import webbrowser
import socket
import tkinter

def print_localIP(path):
    ip = socket.gethostbyname(socket.gethostname())
    with open(path, mode='r+') as f:
        f.write('ip:' + str(ip))
    print(ip)
    return ip

def close_server_and_window(root):
    httpd.shutdown()
    root.destroy()
    sys.exit()

def show_widndowOfIP(ip,PORT,url):
    root = tkinter.Tk()
    root.geometry("400x300")
    #ラベルを追加
    label = tkinter.Label(root, text=str(ip) + ' : ' + str(PORT),font=("",20))
    Button = tkinter.Button(text=u'OPEN')
    Button.bind("<ButtonPress-1>", lambda event: webbrowser.open(url)) #第二引数はeventを引数にとる関数 -> web.open(url)だけだと,それを実行し,そのreturn値(例: 0)を実際の引数とみてしまう(bind("<>", 0) となる)
    #lambda event: webbrowser.open(url) =>
    #   def AAAA(event,url):
    #       webbrowser.open(url)
    # <=== 上記の文章をそのまま入れていると同じ => 関数宣言時に実行されないように,この場合も先に勝手に実行されることはない
    Button2 = tkinter.Button(text=u'CLOSE',command = lambda: close_server_and_window(root))
    #Button2.bind("<ButtonPress-1>", lambda event: close_server_and_window(root))
    #bindだとボタンが押されるエフェクトがない
    label.pack() 
    Button.pack()
    Button2.pack()
    #表示

    root.protocol("WM_DELETE_WINDOW", lambda: close_server_and_window(root))
    root.mainloop()

def server_start(httpd):
    print("serving at port", PORT)
    httpd.serve_forever()  

def inputing_start():
    print('[___end with somekey]')
    if input():
        httpd.shutdown()
        sys.exit()


path = 'info'
PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
#thread_input = threading.Thread(target=inputing_start) #targetは関数名のみ.()をつけると関数が実行され,threadに登録されない,引数はargsにタプルで
thread_server = threading.Thread(target=server_start,args=(httpd,)) # タプル: 1つのみの引数を送るときは [,]をつけ,複数の値とするか, []で長さ1の配列を引数とするか

thread_server.start()
#thread_input.start()
url = "http://localhost:" + str(PORT)
show_widndowOfIP(print_localIP(path),PORT,url)

