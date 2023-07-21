import cv2
import numpy as np
import yaml
from modules.camera.preprocessing.edge_preprocessing import EdgePreprocessor
from modules.camera.preprocessing.image_preprocessing import ImagePreprocessor
from modules.model.detect_w_trt import Detect

with open("config/config.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)
    image, edge = cfg['preprocessing']['image'], cfg['preprocessing']['edge']
    
if __name__ == '__main__':
    imagePreprocessor = ImagePreprocessor(image)
    edgePreprocessor = EdgePreprocessor(edge)
    detection = Detect()
    
    cv2.namedWindow("Calibration")

    # Create trackbars for every attribute
    cv2.createTrackbar("Desired Width", "Calibration", imagePreprocessor.desired_width, 1000, imagePreprocessor.set_desired_width)
    cv2.createTrackbar("Desired Height", "Calibration", imagePreprocessor.desired_height, 1000, imagePreprocessor.set_desired_height)
    cv2.createTrackbar("Alpha", "Calibration", int(imagePreprocessor.alpha * 100), 255, imagePreprocessor.set_alpha)
    cv2.createTrackbar("Beta", "Calibration", int(imagePreprocessor.beta), 127, imagePreprocessor.set_beta)
    
    cv2.imshow("Calibration", np.zeros((1, 500, 3), np.uint8))
    
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        ret, frame = cap.read()
        
        cv2.imshow('Input', frame)

        image = imagePreprocessor.pipeline(frame,
            imagePreprocessor.resize_image,
            imagePreprocessor.flip_image,
            imagePreprocessor.change_contrast_and_brightness,
        )
        
        cv2.imshow('Preprocessed', image)

        detected, results = detection.detection(image)
        print("Results: ", results)
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
    
    cfg['preprocessing']['image'] = imagePreprocessor.get_params()
    cfg['preprocessing']['edge'] = edgePreprocessor.get_params()
    
    # Save changes into existing configuration file .yaml
    with open('config/config.yml', 'w') as f:
        yaml.dump(cfg, f)
        print("Changes saved into config.yml")
