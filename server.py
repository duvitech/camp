#!/usr/bin/env python
"""
Creates an HTTP server with basic auth and websocket communication.
"""
import argparse
import base64
import hashlib
import os
import time
import threading
import webbrowser
import io
import cv2
from PIL import Image
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback

class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")



class WebSocket(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        """Evaluates the function pointed to by json-rpc."""

        # Start an infinite loop when this is called
        if message == "read_camera":
            self.camera_loop = PeriodicCallback(self.loop, 10)
            self.camera_loop.start()

        # Extensibility for other methods
        else:
            print("Unsupported function: " + message)

    def loop(self):
        """Sends camera images in an infinite loop."""
        _, frame = camera.read()
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
        retval, buf = cv2.imencode('.jpg', frame, encode_param)
        if False==retval:
            print('could not encode image!')
        
        # cv2.imshow('Decoded image',buf)
        # cv2.imshow("Image", img)
        # cv2.waitKey(0)
        jpg_as_text = base64.b64encode(buf)
        # print(jpg_as_text[:80])

        try:
            self.write_message(jpg_as_text)
        except tornado.websocket.WebSocketClosedError:
            self.camera_loop.stop()

camera = cv2.VideoCapture(1)
ROOT = os.path.normpath(os.path.dirname(__file__))
resolutions = {"high": (1280, 720), "medium": (640, 480), "low": (320, 240)}

w = 320
h = 240
camera.set(3, w)
camera.set(4, h)


handlers = [(r'/', IndexHandler),
            (r"/websocket", WebSocket),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': ROOT})]

application = tornado.web.Application(handlers)
application.listen(8000)

print('Server started!!')
tornado.ioloop.IOLoop.instance().start()
