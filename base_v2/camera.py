import requests
import cv2
import time
image_url = 'http://127.0.0.1:5000/video_feed'
video_capture = cv2.VideoCapture(2)

start_time = time.time()

while True:
    ret, frame = video_capture.read()
    _, image_data = cv2.imencode('.jpg', frame)
    response = requests.post(image_url, data=image_data.tostring())

    print(response)

    # Every 5 seconds, send a post request to the server
    # if time.time() - start_time > 5:
    #     requests.post('http://127.0.0.1:5000/notification', json={'message': 'Hello, world!'})
    #     start_time = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
