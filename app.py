import asyncio
import os
import yaml
import sys

from aiohttp import client_exceptions
from flask import Flask, render_template, request, json, jsonify
from flask_socketio import SocketIO

from modules.api.apiClient import ApiClient
from modules.cli.cli import cli
from modules.pinOut.pinOut import PinOut
from modules.camera.camera import Camera
from modules.security.security import Security

class App(Camera):
    def __init__(self, client: ApiClient, hardware: dict, camera: int = 0, image_preprocessing_params: dict = None):
        self.client = client
        self.pinOut = PinOut(**hardware)
        self.security = Security()

        # Set RGB led to Green
        self.pinOut.write_rgb(False, True, False)
        super().__init__()
        self.app = Flask(__name__, template_folder='./templates')
        self.socketio = SocketIO(self.app)
        self.routes()
           
    def index(self):
        return render_template('index.html')

    def password(self):
        """
        This method recieve a post request with a password and check if it is correct
        
        Responses:
            - 200: The password is correct
            - 401: The password is incorrect
        """
        data = json.loads(str(request.data)[2:-1])
        password = data['password']
        if self.security.verifyPassword(password):
            self.pinOut.status = 'password'
            return jsonify({'status': 200, 'message': 'Password correct'})
        else:
            return jsonify({'status': 401, 'message': 'Password incorrect'})
            
    def change_password(self):
        """
        This method recieve a post request in JSON format with a password and change the password
        
        Responses:
            - 200: The password is changed
            - 401: The password is incorrect
        """        
        data = json.loads(str(request.data)[2:-1])
        old_password = data['old_password']
        new_password = data['new_password']
        try:
            self.security.validatePassword(new_password)
        except AssertionError:
            return jsonify({'status': 401, 'message': 'Password must be 4 characters long'})
        if not self.security.verifyPassword(old_password):
            return jsonify({'status': 401, 'message': 'Password incorrect'})
        else:
            self.security.changePassword(new_password)
            return jsonify({'status': 200, 'message': 'Password changed'})
    
    def status(self):
        """
        This method recieve a get request and return the status of the system
        or a post request with a status and change the status of the system
        Responses:
            - 200: return the status of the system
        """
        if request.method == 'POST':
            data = json.loads(str(request.data)[2:-1])
            print(data)
            self.pinOut.status = data['status']
            self.weapon = data['weapon'] if 'weapon' in data else None
            if self.pinOut.status == 'sent':
                self.client.new_alert_notification(f"{self.weapon.title()} detected at {self.client.node_config['location']} in node {self.client.node_config['node_id']}")
            return jsonify({'status': 200, 'message': 'Status changed to {}'.format(self.pinOut.status)})
        if request.method == 'GET':
            return jsonify({'status': 200, 'message': self.pinOut.status})
                
    def motion(self):
        """
        This method recieve a get request and return the PIR sensor status
        
        Responses:
            - 200: return the PIR sensor status
        """
        return jsonify({'status': 200, 'message': self.pinOut.read_pin()})
    
    def routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed, methods=['POST'])
        self.app.add_url_rule('/requests', 'tasks', self.tasks, methods=['POST', 'GET'])
        self.app.add_url_rule('/password', 'password', self.password, methods=['POST'])
        self.app.add_url_rule('/change_password', 'change_password', self.change_password, methods=['POST'])
        self.app.add_url_rule('/status', 'status', self.status, methods=['GET', 'POST'])
        self.app.add_url_rule('/motion', 'motion', self.motion, methods=['GET'])

    def run(self, debug=False):
        self.socketio.run(self.app, port=5000, debug=debug)
        
async def main():
    try:
        config = yaml.safe_load(open("config/config.yml"))
        
        # Production
        try:
            client = await cli(
                config['base_url'],
                sys.argv[1],
                sys.argv[2]
                )
        except IndexError:
            print("Please provide username and password")
            sys.exit(1)
        debug = False

        print("Starting flask server...")
        # Send status to server
        app = App(client, config['hardware'], config['camera'], config['preprocessing'])
        await client.patch({'status': True})        

        app.run(debug=debug)
    except client_exceptions.ClientConnectorError:
        print('Server is not available')
    else:        
        # Send status to server
        await client.patch({'status': False})
    finally:
        print("Closing...")
        try:
            app.pinOut.status = 'off'
            app.pinOut.cleanup()
        except:
            pass
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([main()]))
