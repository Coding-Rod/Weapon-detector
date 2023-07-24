import asyncio
import yaml
import sys

from aiohttp import client_exceptions
from flask import Flask
from flask_socketio import SocketIO

from modules.api.apiClient import ApiClient
from modules.cli.cli import cli
from modules.pinOut.pinOut import PinOut
from modules.routes.index import Routes
from modules.security.security import Security

class App(Routes):
    def __init__(self, client: ApiClient, hardware: dict):
        self.client = client
        self.pinOut = PinOut(**hardware)
        self.security = Security()

        # Set RGB led to Green
        self.pinOut.write_rgb(False, True, False)
        super().__init__()
        self.app = Flask(__name__, template_folder='./templates')
        self.socketio = SocketIO(self.app)
        self.routes()
           
    def routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed, methods=['POST'])
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
        debug = True

        print("Starting flask server...")
        # Send status to server
        app = App(client, config['hardware'])
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
