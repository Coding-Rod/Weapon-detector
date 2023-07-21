from flask import Flask, render_template, request
from flask_socketio import SocketIO
import base64
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notification', methods=['POST'])
def notification():
    data = request.get_json()
    # Clear console
    os.system('clear')
    print(data)

@app.route('/video_feed', methods=['POST'])
def image_stream():
    image_data = request.data
    socketio.emit('new_image', {'image': base64.b64encode(image_data).decode('utf-8')})
    return '', 200  # Return a 200 status code to indicate success

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
