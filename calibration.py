import cv2
import numpy as np
import yaml
import time
from modules.preprocessing.background_remover import BackgroundRemover
from modules.preprocessing.image_preprocessing import ImagePreprocessor
# from modules.preprocessing.image_preprocessing import ImagePreprocessor

try:
    from modules.model.detect_w_trt import Detect
except ModuleNotFoundError:
    from modules.model.detect import Detect

with open("config/config.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)
    image = cfg['preprocessing']
    CAMERA = cfg['camera']
    print("Camera:", CAMERA)
    background_threshold = cfg['background_threshold']

if __name__ == '__main__':
    imagePreprocessor = ImagePreprocessor(image)
    background_remover = BackgroundRemover(threshold=background_threshold)
    detection = Detect()
    
    cv2.namedWindow("Calibration")

    # Create trackbars for every attribute
    cv2.createTrackbar("Desired Width", "Calibration", imagePreprocessor.desired_width, 1000, imagePreprocessor.set_desired_width)
    cv2.createTrackbar("Desired Height", "Calibration", imagePreprocessor.desired_height, 1000, imagePreprocessor.set_desired_height)
    cv2.createTrackbar("Alpha", "Calibration", int(imagePreprocessor.alpha * 100), 255, imagePreprocessor.set_alpha)
    cv2.createTrackbar("Beta", "Calibration", int(imagePreprocessor.beta), 127, imagePreprocessor.set_beta)
    cv2.createTrackbar("Bg Threshold", "Calibration", background_remover.threshold, 50, background_remover.set_threshold)
    
    cv2.imshow("Calibration", np.zeros((1, 500, 3), np.uint8))
    
    # Ask user to remove background or not
    bg = input("Remove background? (y/N): ")
    status = 'learning'
    start_bg_time = time.time()
    if CAMERA == 'CSI':
        from utils.csi import gstreamer_pipeline
        cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    else:
        cap = cv2.VideoCapture(CAMERA)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        ret, frame = cap.read()
        
        try:
            cv2.imshow('Input', frame)
        except:
            print(frame)
            continue

        image = imagePreprocessor.pipeline(frame,
            imagePreprocessor.resize_image,
            imagePreprocessor.flip_image,
            imagePreprocessor.change_contrast_and_brightness,
        )
        
        cv2.imshow('Preprocessed', image)
        
        if bg.lower() == 'y':
            if status == 'learning' and (time.time() - start_bg_time) > background_remover.learning_time:
                print("Background learned in ", time.time() - start_bg_time, " seconds")
                status = 'standby'
                background_remover.set_static_background()
                
            elif status == 'learning':
                background_remover.learn_background(image)
                message = "Please be out of the image for " + str(int(background_remover.learning_time - (time.time() - start_bg_time))) + "s"
                image = cv2.putText(image, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                continue
            
            if status == 'standby':
                image = background_remover.remove_background(image)
                print("Background removed")

        detected, results = detection.detection(image)
        # print("Results: ", results)
        if detected:
            print("-"*10, results, "-"*10)
        
        if results:
            try:
                # print(results)
                start_point = int(results[0]['x'] - results[0]['width']//2), int(results[0]['y'] - results[0]['height']//2)
                end_point = int(results[0]['x'] + results[0]['width']//2), int(results[0]['y'] + results[0]['height']//2)
                cv2.rectangle(image, 
                    start_point,
                    end_point,
                    (0, 255, 0),
                    2)
                cv2.putText(image, f"{results[0]['class']}: {results[0]['confidence']}", (start_point[0], start_point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            except (IndexError, KeyError) as e:
                print(e)
        
        # Show the frame
        cv2.imshow('Output', image)
        
        c = cv2.waitKey(1)
        if c == 27: # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    
    cfg['preprocessing'] = imagePreprocessor.get_params()
    cfg['background_threshold'] = background_remover.threshold
    
    # Save changes into existing configuration file .yaml
    with open('config/config.yml', 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False)
        print("Changes saved into config.yml")
