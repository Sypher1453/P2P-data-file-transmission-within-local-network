import http.server
import socketserver
import sys
import threading
import webbrowser
import socket
import tkinter
import urllib.parse
import cgi
from bs4 import BeautifulSoup
import io
from PIL import Image
import base64
import os

class HandleRequests(http.server.BaseHTTPRequestHandler):
    _text = ""

    def _set_content_FILE_paths(self,paths):
        self.paths = paths

    def _set_content(self,content):
        self.html_show = content
        
    def _set_css(self,css):
        self.css_show = css

    def _set_datasPATH(self,filePath):
        self.dataFilePath = filePath

    def _read_ContentsName_inDataPATH(self):
        files = os.listdir(self.dataFilePath)
        # os.path.isfile refers wheteher the argument (ex. "aaa.txt") is on the path of this python-file(ex. "./python") exist
        # so, must set an argument which is shown all-path under the directory python-file existing  
        files_file = [f for f in files if os.path.isfile(self.dataFilePath + '\\' + f)]
        return files_file

    def _set_Content_to_HTML(self):
        get_soup = BeautifulSoup(self.html_show, 'html.parser')
        get_soup.find(id="showArea").string = HandleRequests._text
        get_soup.find(id="css_content").string = self.css_show
        self.html_show = get_soup

    def _write_FILE_onRoot(self,_filename,_fileContent):
        data = open(_filename, "w")
        data.write(_fileContent)
        data.close()
    
    def _read_FILE_onRoot_as_bytes(self,_filename):
        data = open(_filename, "br")
        read_data = data.read()
        data.close()
        return read_data

    def _set_headers(self):
        self.send_response(200)
        #self.send_header('Content-type', 'application/force-download')
        self.send_header('Content-type', 'text/html')
        ###
        #memo:
        #   browse shows the responced-file of first request. the name is the domain-name (ex. localhost:8000)
        #   browser shows the domain-named file, and request another file only if writed on the domain file
        #   so, first resporning header-type must be only text, sound, imag, video. these can be shown 
        # !!!!      if header has two or more content-types, applied only the last type. #!!!!!!!!
        #
        #   if first request (almost get-method) has no above types,
        #   the browser show nothing, and taking process of the request (if has no content-type and has content-disposition, start downloading )
        #   if the request is not correct, start downloadign unccorect fyle named "donload"
        self.end_headers()

    def _set_headers_forceFILE(self,_filename):
        self.send_response(200)
        #self.send_header('Content-type', 'text/html')
        #self.send_header('Content-type', 'application/force-download')
        self.send_header('Content-disposition', 'attachment; filename="' + _filename + '"')
        self.end_headers

    def do_GET(self):
        ##
        # if call the source in HTML (ex. <src = "/a.txt">),browser call the get-requset to the URL (ex. localhost:8000/a.txt)
        # every access to directly and file-name under this domein, the access access to this do-GET method without action = "post" 
        # then need to separate proccesses by filenames (ex. aa.html -> html-file to respon, /abc -> html-file to respon, ba.img -> send img-file to respon)
        # the returned value is named on the browser tab (ex. request: src="~~/a.txt", return: "aaaabb", then: ~~/a.txt="aaaabb"  in the tab)
        #   so, only one do-get process, and requests are various (css, html,js,img), then all files have same content

        # ONE request, ONE respon ----- can't return multi resupone(CAN'T: one request -> return: (header1,body1),(header2,body2))
        # maybe multi respons is ignored without first respon, maybe criant shut out the resporns after got a resporn of first. 
        ##
        # browser reloading request the same method of domain-named files method (if the file was loaded by post, then request post-method,if get, then get-method)
        print(self.path)
        print(self.headers)
        if self.path.endswith(".css"):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(self._read_FILE_onRoot_as_bytes(self.path[1:]))
        elif self.path.endswith(".png"):
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(base64.b64encode(self._read_FILE_onRoot_as_bytes("adafafdafa.png")))
        else:
            global _text
            #self._read_Content_inTmpFILE()
            get_soup = BeautifulSoup(self.html_show, 'html.parser')
            get_soup.find(id="showArea").string =  HandleRequests._text
            #get_soup.find(id="css_content").string = self.css_show
            self.html_show = get_soup
            ##self._set_Content_to_HTML()
            self._set_headers()
            self.wfile.write(self.html_show.encode())


        
    def do_POST(self):
        global _text
        file_names = []
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            length = int(self.headers['content-length'])
            fp = io.BytesIO(self.rfile.read(length))
            environ = {'REQUEST_METHOD': 'POST'}
            postvars = cgi.FieldStorage(fp=fp, environ=environ, headers=self.headers)
            for f in postvars.list:
                print(f.type)
                file_names.append(f.filename)
                if 'image' in f.type:
                    pg = io.BytesIO(f.value)
                    img = Image.open(pg)
                    img.save(self.dataFilePath + f.filename,f.type[6:])
                elif 'text' in f.type:
                    self._write_FILE_onRoot(self.dataFilePath + f.filename,f.value.decode())
                    
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = urllib.parse.parse_qs(self.rfile.read(length).decode(), keep_blank_values=1)
            #.decode() is for decoding. if not use, postvars' tag and value is writen on bytes-type ("aaa" -> b"aaa")(type: str -> bytes). bytes-type works on ascii
        else:
            postvars = {}

        if ctype == 'application/x-www-form-urlencoded':
            #print(postvars['text'][0])

            _text = postvars['text'][0]
            ##
            #soup = BeautifulSoup(self.html_show, 'html.parser')
            ###_text = soup.find(id="showArea")
            ###_text.string = str(postvars)
            #soup.find(id="showArea").string = postvars['text'][0]
            #self.html_show = soup
            #self._set_headers()
            #self.wfile.write(self.html_show.encode())
            ##
            # These are for form-button(return html-source to cliant and load-and-show the returned data(the html-source in this case) on cliant, on clicking form-button)
            # so using above construction, can move to another page with clicking form-button

            # under case, return the text-data got. so if using form-button, show only the text-data. should xml to show the data on correct area.

            self._set_headers()
            self.wfile.write(postvars['text'][0].encode())
            ##self._write_Content_toTMP(postvars['text'][0])
        elif ctype == 'multipart/form-data':
            #self._read_Content_inTmpFILE()
            #get_soup = BeautifulSoup(self.html_show, 'html.parser')
            #get_soup.find(id="showArea").string = self._readContents
            #get_soup.find(id="css_content").string = self.css_show
            #self.html_show = get_soup

            ##self._set_Content_to_HTML()
            #get_soup = BeautifulSoup(self.html_show, 'html.parser')
            #get_soup.find(id="showArea").string =  _text
            #get_soup.find(id="css_content").string = self.css_show
            #get_soup.find(id="free").string = files[0].filename
            #get_soup.find(id="free").name = ("a id = \"free\" href=\"" + "/" + files[0].filename + "\" download=\"" + files[0].filename + "\"")
            #get_soup.find(id="free").string = "<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=" + files[0].filename + "\">"
            #self.html_show = get_soup
            _sendable_fileNames = ','.join(self._read_ContentsName_inDataPATH())
            self._set_headers()
            #self._set_headers_forceFILE(files[0].filename)
            #self.wfile.write(self.html_show.encode())
            self.wfile.write(_sendable_fileNames.encode())
        #'''Reads post request body'''
        #self._set_headers()
        #content_len = int(self.headers.getheader('content-length', 0))
        #post_body = self.rfile.read(content_len)
        #self.wfile.write("received post request:<br>{}".format(post_body))

    #def do_PUT(self):
    #    self.do_POST()


def load_html(path):
    test_data = open(path, "r")

    contents = test_data.read()

    test_data.close()
    return contents

def write_data(path,_content):
    test_data = open(path, "a")
    contents = test_data.write(_content)
    test_data.close()


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
    Button = tkinter.Button(text=u'OPEN',command = lambda: webbrowser.open(url))
    ###Button = tkinter.Button(text=u'OPEN')
    ###Button.bind("<ButtonPress-1>", lambda event: webbrowser.open(url)) #第二引数はeventを引数にとる関数 -> web.open(url)だけだと,それを実行し,そのreturn値(例: 0)を実際の引数とみてしまう(bind("<>", 0) となる)
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

html_path = './index.html'
html_content = load_html(html_path)
css_path = './main.css'
css_content = load_html(css_path)
path = 'info'
PORT = 8000
#Handler = http.server.SimpleHTTPRequestHandler
Handler = HandleRequests
Handler._set_content(Handler,html_content)
Handler._set_css(Handler,css_content)
Handler._set_datasPATH(Handler,"./data")

httpd = socketserver.TCPServer(("", PORT), Handler)
#thread_input = threading.Thread(target=inputing_start) #targetは関数名のみ.()をつけると関数が実行され,threadに登録されない,引数はargsにタプルで
thread_server = threading.Thread(target=server_start,args=(httpd,)) # タプル: 1つのみの引数を送るときは [,]をつけ,複数の値とするか, []で長さ1の配列を引数とするか

thread_server.start()
#thread_input.start()
url = "http://localhost:" + str(PORT)
show_widndowOfIP(print_localIP(path),PORT,url)


## tmp-file vs global-variable
## lookable vs low codes
## low memori vs fast load,fast quit
## savable  vs  unsavable
