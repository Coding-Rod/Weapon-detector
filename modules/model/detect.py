import numpy as np
import subprocess
from collections import deque
import base64
import json
import cv2

class Detect:
    curl_command = 'curl --silent -d "@-" "http://localhost:9001/knives-n-guns-backup/1?api_key=uWT4WzrPNeKaypAQ3Ah7"'
    thresholds = [0.95, 0.77]
    queues = [deque(maxlen=8), deque(maxlen=8)]
    constant = 0.2
        
        
    def momentum(self, class_name: int, confidence: float, threshold: float, queue: deque, constant: float = 0.9, verbose: bool = False) -> tuple:
        """ Momentum is a measure of how many frames in a row a given class has been, it considers a queue of the last 10 frames and returns the most frequent class in the queue, consudering a pondered sum of the last 10 frames. Each frame has a weight of a constant value between 0 and 1, where the first frame has the lowest weight confidense multiplied by the constant power to n, where n is the frame index, and the last frame has the highest weight confidense multiplied by the constant power to 0.

        Args:
            class_name (int): Class name, could be 0 or 1, where 0 is no class and 1 is class.
            confidence (float): Confidence of the class, between 0 and 1.

        Returns:
            int: Class name, could be 0 or 1, where 0 is no class and 1 is class.
        """
        momentum = 0
        queue.append((class_name, confidence))
        
        for i,j in enumerate(queue):
            momentum += j[0] * (j[1] * constant ** i )

        if verbose:
            print("Queue: ", queue, end=" ")
            print("Momentum: ", momentum, end=" ")

        return momentum >= threshold, queue
    
    def detection(self, frame: np.ndarray) -> list:
        """ This function is used to detect weapons in a frame

        Args:
            frame (np.ndarray): The frame to be processed

        Returns:
            list: The list of detected weapons with their classes and amounts
        """
        
        frame = cv2.flip(frame, 0)

        frame = cv2.resize(frame, (640, 640))

        # Convert the frame to base64
        _, img_encoded = cv2.imencode(".jpg", frame)
        base64_data = base64.b64encode(img_encoded).decode("utf-8")

        # Run the curl command and pass the base64 data as input
        process = subprocess.Popen(self.curl_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        stdout, _ = process.communicate(input=base64_data.encode('utf-8'))

        # Decode the response
        response = stdout.decode('utf-8')

        try:        
            # Getting predictions
            bounding_boxes_text = response.split('predictions": ')[1].split('],')[0] + ']'
            
            # Converting to list
            bounding_boxes = json.loads(bounding_boxes_text)
            
            bounding_boxes = bounding_boxes or [{'class': None, 'confidence': 0}]
            
            # Check momentums
            for i, threshold in enumerate(self.thresholds):
                for bounding_box in bounding_boxes:
                    class_name = bounding_box['class']
                    confidence = bounding_box['confidence']
                    momentum_result, self.queues[i] = self.momentum(1 if class_name else 0, float(confidence), float(threshold), self.queues[i], self.constant, verbose=True)
                    
                    print("Class: ", class_name, end=' ')
                    print("Momentum: ", momentum_result)
                    
                    if momentum_result:
                        print("Weapon detected")
                        self.queues[0].clear()
                        self.queues[1].clear()
                        return {
                            ('knives', 'guns')[int(class_name == 'gun')]: 1,
                            ('knives', 'guns')[int(class_name != 'gun')]: 0,
                        }
            
            
        except IndexError:
            print("response: ", response)
            return