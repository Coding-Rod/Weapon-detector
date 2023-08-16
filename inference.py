import requests
import cv2
import time
import sys
import yaml
import datetime
import os

try:
    from modules.model.detect_w_trt import Detect
except ModuleNotFoundError:
    from modules.model.detect import Detect
from modules.preprocessing.image_preprocessing import ImagePreprocessor
from modules.preprocessing.background_remover import BackgroundRemover

time.sleep(5)

with open('config/config.yml') as f:
    config = yaml.safe_load(f)
    CAMERA = config['camera']
    background_threshold = config['background_threshold']
weapon = None
last_weapon = None
global_time = time.time()
class APIHandler:
    server_url = 'http://127.0.0.1:5000'
    prev_status = None

    def get_status(self):
        attempt = 0
        while True:
            response = requests.get(self.server_url + '/status')
            try:
                result = response.json()['message']
                return result
            except Exception as e:
                print(e)
                attempt += 1
                if attempt > 10:
                    raise Exception("Server not responding")
                time.sleep(1)            

    @property
    def status(self):
        return self.prev_status if self.prev_status else self.get_status()

    @status.setter
    def status(self, status):
        global weapon, last_weapon, global_time
        # print("Time: ", time.time() - global_time)
        data ={
            'status': status,
        }
        
        weapon = weapon if weapon else last_weapon
        if status == 'sent':
            data = {
                **data,
                "weapon": weapon
            }
            
        if self.prev_status != status:
            global_time = time.time()
            response = requests.post(self.server_url + '/status', json=data)
            self.prev_status = status
            print(response.json()['message'])
    @property
    def motion(self):
        response = requests.get(self.server_url + '/motion')
        return response.json()['message']
    
class StreamHandler:
    if CAMERA == 'CSI':
        from utils.csi import gstreamer_pipeline
        video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    else:
        video_capture = cv2.VideoCapture(CAMERA)
        
    def convert_to_bytes(self, frame):
        _, image_data = cv2.imencode('.jpg', frame)
        return image_data.tostring()
        
    def get_frame(self):
        _, frame = self.video_capture.read()
        return frame
    
    def send_frame(self, image):
        response = requests.post(self.image_url, data=self.convert_to_bytes(image))
        return response

class ImageHandler:
    config = yaml.safe_load(open("config/config.yml"))
    imagePreprocessor = ImagePreprocessor(config['preprocessing'])
    backgroundRemover = BackgroundRemover(threshold=background_threshold)   
    
    def preprocess(self, image):
        try:
            return self.imagePreprocessor.pipeline(image,
                self.imagePreprocessor.resize_image,
                self.imagePreprocessor.flip_image,
                self.imagePreprocessor.change_contrast_and_brightness,
            )
        except cv2.error as e:
            print(e)
            return image
    
    def background_removal(self, image):
        print("Removing bg...")
        return self.backgroundRemover.remove_background(image)
    
    def background_learning(self, frame):
        if self.status == 'standby' and (time.time() - self.start_bg_time) > 300:
            self.status = 'learning'
            self.start_bg_time = time.time() # Reset start time for background learning
        
        elif self.status == 'learning' and (time.time() - self.start_bg_time) > self.backgroundRemover.learning_time:
            print("Background learned in ", time.time() - self.start_bg_time, " seconds")
            self.status = 'standby'
            self.backgroundRemover.set_static_background()
            
        elif self.status == 'learning':
            self.backgroundRemover.learn_background(frame)
            message = "Please be out of the frame for " + str(int(self.backgroundRemover.learning_time - (time.time() - self.start_bg_time))) + "s"
            frame = cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)

            if self.motion:
                print("Motion detected while learning background")
                print("Background learning stopped")
                self.status = 'standby'
        return frame
        
class InferenceHandler(APIHandler, StreamHandler, ImageHandler):
    detection = Detect()
    
    def __init__(self):
        global global_time
        self.image_url = self.server_url + '/video_feed'
        while self.status not in ['standby', 'learning', 'starting', 'running', 'sent', 'alarm', 'password']:
            print('Waiting for server...')
            time.sleep(1)
        print('Server is ready!')
        self.status = 'learning'
        self.start_bg_time = time.time()
        global_time = time.time()
    
    def state_machine(self) -> bool:
        """ The state machine for the pin.
        
        Returns:
            bool: If system should be in weapon detection mode.
        """
        global global_time
        if self.status == 'standby' and self.motion:
            self.status = 'running' # Set status to running
        
        elif self.status == 'running' and (time.time() - global_time) > 12:
            self.status = 'standby' # Set status to standby
        
        elif self.status == 'sent' and time.time() - global_time > 15:
            self.status = 'alarm' # Set status to alarm
        
        elif (self.status == 'alarm' and time.time() - global_time > 60) or self.status == 'password':
            self.status = 'standby' # Set status to standby
        
        if self.status == 'running':
            return True # Return True
        else:
            return False # Return False
    
    def obj_detect(self, image):
        return self.detection.detection(image)

if __name__ == '__main__':
    try:
        inferenceHandler = InferenceHandler()
        status = inferenceHandler.status
        # print("Status: ", status)
        if status not in ['standby', 'learning', 'starting', 'running', 'sent', 'alarm', 'password']:
            print("Server connection not established")
            sys.exit(1)
        while True:
            start_time = time.time()
            # print("Status: ", inferenceHandler.status)
            frame = inferenceHandler.get_frame()
            frame = inferenceHandler.preprocess(frame)
            weapon_detection = inferenceHandler.state_machine()
            frame = inferenceHandler.background_learning(frame)
            detected = False
            
            if weapon_detection: # If motion is detected
                try:
                    frame_wo_bg = inferenceHandler.background_removal(frame)
                except Exception as e:
                    print(e)
                detected, results = inferenceHandler.obj_detect(frame_wo_bg)
                # print("Detected: ", detected)
                # print("Results: ", results)
                
                try:
                    cv2.imshow('proprocessed frame', frame_wo_bg)
                except cv2.error as e:
                    pass
                    
                if detected:
                    weapon = results[0]['class']
                    inferenceHandler.status = 'sent'
                    
                    print("-"*10, results, "-"*10)
                    
                    # raise Exception("Weapon detected")
                    weapon_detection = False
                
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
                        last_weapon = results[0]['class']
                    except (IndexError, KeyError) as e:
                        print(e)
            if detected:
                now = datetime.datetime.now()
                p = os.path.sep.join(['images', "img_{}.png".format(str(now).replace(":",''))])
                cv2.imwrite(p, frame)
            
            if inferenceHandler.status == 'sent':
                message = f"Alarm will sound in {15 - int(time.time() - global_time)} seconds"
                cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                
            if inferenceHandler.status == 'alarm' or inferenceHandler.status == 'sent':
                inferenceHandler.status = inferenceHandler.get_status()
            
            # print("Inference time: ", time.time() - global_time)
            # Add fps to right bottom corner
            fps = round(1.0 / (time.time() - start_time),2)
            cv2.putText(frame, f"FPS: {fps}", (frame.shape[1] - 170, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            inferenceHandler.send_frame(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except requests.exceptions.ConnectionError:
        print("Server is not running\nPress Ctrl+C to exit")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Inference finished succesfully!")
        sys.exit(1)
