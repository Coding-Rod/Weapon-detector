import cv2
import numpy as np
import yaml
from modules.camera.preprocessing.edge_preprocessing import EdgePreprocessor
from modules.camera.preprocessing.image_preprocessing import ImagePreprocessor

with open("config/config.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)
    image, edge = cfg['preprocessing']['image'], cfg['preprocessing']['edge']
    
if __name__ == '__main__':
    imagePreprocessor = ImagePreprocessor(image)
    edgePreprocessor = EdgePreprocessor(edge)
    
    cv2.namedWindow("Calibration")

    # Create trackbars for every attribute
    cv2.createTrackbar("Desired Width", "Calibration", imagePreprocessor.desired_width, 1000, imagePreprocessor.set_desired_width)
    cv2.createTrackbar("Desired Height", "Calibration", imagePreprocessor.desired_height, 1000, imagePreprocessor.set_desired_height)
    cv2.createTrackbar("Clip Limit", "Calibration", int(edgePreprocessor.clip_limit * 100), 1000, edgePreprocessor.set_clip_limit)
    cv2.createTrackbar("Tile Grid Size Width", "Calibration", edgePreprocessor.tile_grid_size[0], 128, edgePreprocessor.set_tile_grid_size_width)
    cv2.createTrackbar("Tile Grid Size Height", "Calibration", edgePreprocessor.tile_grid_size[1], 128, edgePreprocessor.set_tile_grid_size_height)
    cv2.createTrackbar("Canny Threshold 1", "Calibration", edgePreprocessor.canny_threshold1, 255, edgePreprocessor.set_canny_threshold1)
    cv2.createTrackbar("Canny Threshold 2", "Calibration", edgePreprocessor.canny_threshold2, 255, edgePreprocessor.set_canny_threshold2)
    cv2.createTrackbar("Color Red Channel", "Calibration", edgePreprocessor.color[0], 255, edgePreprocessor.set_red_color)
    cv2.createTrackbar("Color Green Channel", "Calibration", edgePreprocessor.color[1], 255, edgePreprocessor.set_green_color)
    cv2.createTrackbar("Color Blue Channel", "Calibration", edgePreprocessor.color[2], 255, edgePreprocessor.set_blue_color)
    cv2.createTrackbar("Lines Threshold", "Calibration", edgePreprocessor.lines_threshold, 255, edgePreprocessor.set_lines_threshold)
    cv2.createTrackbar("Lines Min Line Length", "Calibration", edgePreprocessor.lines_min_line_length, 255, edgePreprocessor.set_lines_min_line_length)
    cv2.createTrackbar("Lines Max Line Gap", "Calibration", edgePreprocessor.lines_max_line_gap, 255, edgePreprocessor.set_lines_max_line_gap)
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
            imagePreprocessor.change_contrast_and_brightness,
        )
        
        cv2.imshow('Preprocessed', image)

        result = edgePreprocessor.pipeline(image,
            edgePreprocessor.convert_to_grayscale,
            edgePreprocessor.apply_clahe,
            # preprocessor.perform_histogram_equalization,
            edgePreprocessor.detect_edges,
            edgePreprocessor.detect_lines, # Filtro pasobajas
            edgePreprocessor.dilate_image,
            edgePreprocessor.invert_image,
        )
        # Inverted edges
        cv2.imshow('Edges', cv2.bitwise_not(edgePreprocessor.get_edges()))
        
        # result = preprocessor.get_preprocessed_image_with_original(frame)
        cv2.imshow('Result', result)
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
