#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 08:13:43 2017
@author: dc
"""
 
from urllib import request
import http.server as hs
import sys, os, urllib
import numpy as np
import cv2
import json
import qrtailoringdiscern
import hashlib

class ServerException(Exception):
    '''服务器内部错误'''
 
    pass
 
 
class RequestHandler(hs.BaseHTTPRequestHandler):
 
    def send_content(self, page, status=200):
 
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(bytes(page, encoding='utf-8'))
        # print(page)
 
    def do_GET(self):
        print("---doget")
        if self.path == "/favicon.ico":
            rejson = {'status':'500'}
        imgurl = ""
        if '?' in self.path:#如果带有参数     
            self.queryString=urllib.parse.unquote(self.path.split('?',1)[1])
            params=urllib.parse.parse_qs(self.queryString)
            imgurl = params["imgurl"][0]
        if imgurl == "":
            rejson = {'status':'500'}
        else:
            resp = request.urlopen(imgurl)
            img = np.asarray(bytearray(resp.read()), dtype="uint8")
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)
            #img = cv2.imread("3.jpg")
            # 初始化cv2的二维码检测器
            detector = cv2.QRCodeDetector()
            # 解码
            data, bbox, straight_qrcode = detector.detectAndDecode(img)
            # 如果解码成功
            if bbox is not None:
                print(f"QRCode data:\n{data}")
                # 用线条显示图像
                # 边框长度
                n_lines = len(bbox)
                for i in range(n_lines):
                    # 输出
                    point1 = tuple(bbox[i][0])
                    point2 = tuple(bbox[(i + 1) % n_lines][0])
                    cv2.line(img, point1, point2, color=(255, 0, 0), thickness=2)
            if data is not None:
                filename = hashlib.md5(imgurl).hexdigest()+".jpg"
                image = qrtailoringdiscern.reshape_image(img)
                image,contours,hierachy = qrtailoringdiscern.detecte(image)
                data = qrtailoringdiscern.find(image,filename,contours,np.squeeze(hierachy))
                print(f"test:\n{data}")
            rejson = {'status':'200','qrcode':data} 
        self.send_content(json.dumps(rejson) , 200)
    def handle_file(self, full_path):
        print("---handle_file")

        self.send_content("---youok11" , 200)
    Error_Page = """\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    """
 
    def handle_error(self, msg):
 
        content = self.Error_Page.format(path=self.path, msg=msg)
 
        self.send_content(content, 404)
 
 
if __name__ == '__main__':
    httpAddress = ('', 8081)
    httpd = hs.HTTPServer(httpAddress, RequestHandler)
    httpd.serve_forever()