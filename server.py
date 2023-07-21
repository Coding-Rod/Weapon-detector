from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
import cv2
import io
import sys
import imutils
import json
import base64

from modules.model.yoloDet import YoloTRT

HOST_NAME = 'localhost'
PORT_NUMBER = 9001

class ImageHandler(BaseHTTPRequestHandler):
    model = YoloTRT(library="modules/model/yolov5/build/libmyplugins.so", engine="modules/model/yolov5/build/yolov5.engine", conf=0.1, yolo_ver="v5")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Decode the base64 image data
        image_data = base64.b64decode(post_data)

        # Convert the image data to numpy array
        nparr = np.frombuffer(image_data, np.uint8)

        # Read the image using cv2
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Use detection model to process the image
        detections, t = self.model.Inference(image) # returns detections and inference time
        
        # Convert every np.ndarray to list
        detections = [{**detection, 'box': detection['box'].tolist()} for detection in detections]
        
        # Convert bounding boxes to JSON
        json_data = json.dumps(str(detections))
        
        # Print bounding boxes
        print("Bounding boxes: ", json_data)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT_NUMBER), ImageHandler)
    print(f"Server running on http://{HOST_NAME}:{PORT_NUMBER}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\nServer stopped.")
