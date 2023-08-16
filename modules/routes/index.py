import base64
import json
from flask import request, jsonify, render_template

class Routes:
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
            self.pinOut.status = data['status']
            self.weapon = data['weapon'] if 'weapon' in data else None
            if self.pinOut.status == 'sent':
                message = ' '.join([
                    self.weapon.title(),
                    'detected at',
                    self.client.node_config['name'],
                    '-',
                    self.client.node_config['location'],
                    'by node',
                    str(self.client.node_config['node_id'])
                ])
                self.client.new_alert_notification(message)
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
    
        
    def video_feed(self):
        """ This method recieve a post request with an image and send it to the client

        Returns:
            _type_: Return a 200 status code to indicate success
        """        
        image_data = request.data
        self.socketio.emit('new_image', {'image': base64.b64encode(image_data).decode('utf-8')})
        return '', 200  # Return a 200 status code to indicate success