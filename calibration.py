import cv2
import numpy as np

from modules.camera.preprocessing.edge_preprocessing import EdgePreprocessor
from modules.camera.preprocessing.image_preprocessing import ImagePreprocessor

if __name__ == '__main__':
    edgePreprocessor = EdgePreprocessor()
    imagePreprocessor = ImagePreprocessor()
    
    cv2.namedWindow("Calibration")

    # Create trackbars for every attribute
    cv2.createTrackbar("Desired Width", "Calibration", edgePreprocessor.desired_width, 1000, edgePreprocessor.set_desired_width)
    cv2.createTrackbar("Desired Height", "Calibration", edgePreprocessor.desired_height, 1000, edgePreprocessor.set_desired_height)
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
    cv2.createTrackbar("Alpha", "Calibration", int(imagePreprocessor.alpha * 100), 200, imagePreprocessor.set_alpha)
    cv2.createTrackbar("Beta", "Calibration", int(imagePreprocessor.beta), 255, imagePreprocessor.set_beta)
    
    cv2.imshow("Calibration", np.zeros((1, 500, 3), np.uint8))
    
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        ret, frame = cap.read()
        
        cv2.imshow('Input', frame)

        image = imagePreprocessor.pipeline(frame,
            imagePreprocessor.change_contrast_and_brightness,
        )
        
        cv2.imshow('Preprocessed', image)

        result = edgePreprocessor.pipeline(image,
            edgePreprocessor.resize_image,
            edgePreprocessor.convert_to_grayscale,
            edgePreprocessor.apply_clahe,
            # preprocessor.perform_histogram_equalization,
            edgePreprocessor.detect_edges,
            edgePreprocessor.detect_lines,
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
    
    # Save changes into .env file
    with open('.env', 'w') as f:
        f.write(f"DESIRED_WIDTH={edgePreprocessor.desired_width}\n")
        f.write(f"DESIRED_HEIGHT={edgePreprocessor.desired_height}\n")
        f.write(f"CLIP_LIMIT={edgePreprocessor.clip_limit}\n")
        f.write(f"TILE_GRID_SIZE={edgePreprocessor.tile_grid_size_width},{edgePreprocessor.tile_grid_size_height}\n")
        f.write(f"CANNY_THRESHOLD={edgePreprocessor.canny_threshold1},{edgePreprocessor.canny_threshold2}\n")
        f.write(f"COLOR={edgePreprocessor.color[0]},{edgePreprocessor.color[1]},{edgePreprocessor.color[2]}\n")
        f.write(f"LINES={edgePreprocessor.lines_threshold},{edgePreprocessor.lines_min_line_length},{edgePreprocessor.lines_max_line_gap}\n")
        f.write(f"ALPHA={imagePreprocessor.alpha}\n")
        f.write(f"BETA={imagePreprocessor.beta}\n")