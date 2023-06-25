import asyncio
import yaml
import os

from aiohttp import client_exceptions
from flask import Flask, render_template, request, json, jsonify
from getpass import getpass

from modules.api.apiClient import ApiClient
from modules.cli.cli import cli
from modules.pinOut.pinOut import PinOut
from modules.camera.camera import Camera
from modules.security.security import Security

class App(Camera):
    def __init__(self, client: ApiClient, hardware: dict, camera: int = 0):
        self.client = client
        self.pinOut = PinOut(**hardware)
        self.security = Security()

        # Set RGB led to Green
        self.pinOut.write_rgb(False, True, False)
        super().__init__(camera)
        self.app = Flask(__name__, template_folder='./templates')
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
        data = json.loads(str(request.data))
        password = data['password']
        if self.security.verifyPassword(password):
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
        data = json.loads(str(request.data))
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
            
    def routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)
        self.app.add_url_rule('/requests', 'tasks', self.tasks, methods=['POST', 'GET'])
        self.app.add_url_rule('/password', 'password', self.password, methods=['POST'])
        self.app.add_url_rule('/change_password', 'change_password', self.change_password, methods=['POST'])

    def run(self, debug=False):
        if debug:
            self.app.run(debug=debug, threaded=True, use_reloader=False)
        else:
            self.app.run()
         
async def main():
    try:
        config = yaml.safe_load(open("config/config.yml"))
        
        # Clear terminal
        os.system('clear')
        
        print("Welcome to the crime detection system controller")
        print("Please your username and password to start the system")
        
        # Development
        client = await cli(
            config['base_url'],
            'rod5919',
            'password123'
        )
        
        # Production
        # client = await cli(
        #     config['base_url'],
        #     input("Username: "),
        #     getpass("Password: ")
        #     )

        print("Starting...")
        # Send status to server
        app = App(client, config['hardware'], config['camera'])
        await client.patch({'status': True})        

        app.run(debug=True)
    except client_exceptions.ClientConnectorError:
        print('Server is not available')
    else:        
        # Send status to server
        await client.patch({'status': False})
    finally:
        print("Closing...")
        try:
            app.cleanup()
        except UnboundLocalError:
            pass
        try:
            app.pinOut.write_rgb(False, False, False)
            app.pinOut.write_relay(False)
            app.pinOut.cleanup()
        except:
            pass
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([main()]))