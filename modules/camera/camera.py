import cv2
import os
import datetime
import time
from flask import render_template, Response, request
from threading import Thread

from ..model.detect_opt import Detect
from .preprocessing.image_preprocessing import ImagePreprocessor
from .preprocessing.background_remover import BackgroundRemover

class Camera(Detect):
    def __init__(self, camera: int = 0, image_preprocessing_params: dict = None):
        self.capture = 0
        self.rec = 0
        self.rec_frame = None
        self.out = None
        self.camera = None
        self.start_bg_time = 0
        self.imagePreprocessor = ImagePreprocessor(image_preprocessing_params)
        self.background_remover = BackgroundRemover()
        self.setup(camera)
    
    def setup(self, camera: int):
        os.makedirs('images', exist_ok=True)
        os.makedirs('videos', exist_ok=True)

        self.camera = cv2.VideoCapture(camera)
    
    def gen_frames(self):
        """ Generate the frames for the video stream.

        Yields:
            _type_: The frame of the video stream.
        """
        
        # Set start fps time
        start_fps_time = time.time()
        
        # Set the status to standby
        self.pinOut.status = 'learning'
        self.start_bg_time = time.time()
        
        while True:
            # print("Time: ", time.time() - self.start_time, " Status: ", self.pinOut.status)
            success, frame = self.camera.read()
            
            try:
                frame = self.imagePreprocessor.pipeline(frame,
                    self.imagePreprocessor.resize_image,
                    self.imagePreprocessor.flip_image,
                    self.imagePreprocessor.change_contrast_and_brightness,
                )
                
            except cv2.error:
                print("Camera is not available")
            
            weapon_detection = self.pinOut.state_machine()
            # region: Background removal
            
            if self.pinOut.status == 'standby' and (time.time() - self.start_bg_time) > 300:
                self.pinOut.status = 'learning'
                self.start_bg_time = time.time() # Reset start time for background learning
            
            elif self.pinOut.status == 'learning' and (time.time() - self.start_bg_time) > self.background_remover.learning_time:
                print("Background learned in ", time.time() - self.start_bg_time, " seconds")
                self.pinOut.status = 'standby'
                self.background_remover.set_static_background()
                
            elif self.pinOut.status == 'learning':
                message = "Please be out of the frame for " + str(int(self.background_remover.learning_time - (time.time() - self.start_bg_time))) + "s"
                frame = cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                self.background_remover.learn_background(frame)

                if weapon_detection:
                    print("Motion detected while learning background")
                    print("Background learning stopped")
                    self.pinOut.status = 'standby'
                
            # endregion: Background removal
            
            if success:
                if weapon_detection: # If motion is detected
                    try:
                        frame_wo_bg = self.background_remover.remove_background(frame)
                    except Exception as e:
                        print(e)
                    detected, results = self.detection(frame_wo_bg)
                    try:
                        cv2.imshow('proprocessed frame', frame_wo_bg)
                    except cv2.error as e:
                        pass
                        
                    if detected:
                        self.pinOut.status = 'sent'
                        
                        print("-"*10, results, "-"*10)
                        weapon = results[0]['class']
                        try:
                            self.client.new_alert_notification(f"{weapon.title()} detected at {self.client.node_config['location']} in node {self.client.node_config['node_id']}")
                        except AttributeError:
                            self.pinOut.status = 'standby'
                        # raise Exception("Weapon detected")
                        weapon_detection = False
                        self.capture = 1
                        self.start_bg_time = time.time()
                    
                    if results:
                        try:
                            # print(results)
                            start_point = int(results[0]['x'] - results[0]['width']//2), int(results[0]['y'] - results[0]['height']//2)
                            end_point = int(results[0]['x'] + results[0]['width']//2), int(results[0]['y'] + results[0]['height']//2)
                            cv2.rectangle(frame, 
                                start_point,
                                end_point,
                                (0, 255, 0),
                                2)
                            cv2.putText(frame, f"{results[0]['class']}: {results[0]['confidence']}", (start_point[0], start_point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        except (IndexError, KeyError) as e:
                            print(e)
                    
                if self.pinOut.status == 'sent':
                    message = f"Alarm will sound in {15 - int(time.time() - self.start_bg_time)} seconds"
                    cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                
                if self.capture:
                    self.capture = 0
                    now = datetime.datetime.now()
                    p = os.path.sep.join(['images', "img_{}.png".format(str(now).replace(":", ''))])
                    cv2.imwrite(p, frame)

                if self.rec:
                    self.rec_frame = frame
                    frame = cv2.putText(
                        cv2.flip(frame, 1), "Recording...", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4
                    )
                    frame = cv2.flip(frame, 1)

                try:
                    # Calculate fps
                    fps = 10 / (time.time() - start_fps_time)
                    
                    # Write fps to frame (bottom right corner)
                    frame = cv2.putText(frame, f"FPS: {fps:.2f}", (frame.shape[1] - 150, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                except Exception as e:
                    pass
            else:
                pass
    
    def video_feed(self):
        return Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
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
    
    def cleanup(self):
        self.camera.release()
        cv2.destroyAllWindows()
