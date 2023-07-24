import base64
import cv2
import os
import datetime
import time
from flask import render_template, request
from threading import Thread

class Camera:
    capture = 0
    rec = 0
    rec_frame = None
    out = None
    
    def __init__(self):
        os.makedirs('images', exist_ok=True)
        os.makedirs('videos', exist_ok=True)
        
    def video_feed(self):
        """ This method recieve a post request with an image and send it to the client

        Returns:
            _type_: Return a 200 status code to indicate success
        """        
        image_data = request.data
        self.socketio.emit('new_image', {'image': base64.b64encode(image_data).decode('utf-8')})
        return '', 200  # Return a 200 status code to indicate success
    
    def record(self, out: cv2.VideoWriter):
        while self.rec:
            time.sleep(0.05)
            out.write(self.rec_frame)

    def tasks(self):
        if request.method == 'POST':
            if request.form.get('click') == 'Capture':
                self.capture = 1
            elif request.form.get('rec') == 'Start/Stop Recording':
                self.rec = not self.rec
                if self.rec:
                    now = datetime.datetime.now()
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    self.out = cv2.VideoWriter('./videos/vid_{}.mp4'.format(str(now).replace(":", '')), fourcc, 20.0, (640, 480))
                    # Start new thread for recording the video
                    thread = Thread(target=self.record, args=[self.out, ])
                    thread.start()
                elif not self.rec:
                    self.out.release()

        return render_template('index.html')
    
