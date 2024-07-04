from flask import Flask, request, jsonify
import subprocess
import os
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some-super-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow specific origin
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow specific origin

printer_name = "EPSON TM-T88V Receipt"
file_path = r"c:\users\kiosk-1\desktop\printfile.txt"

@app.route('/api/data', methods=['GET'])
def get_data():
    return 'data'

@socketio.on('sandwich')
def handle_sandwich_event(data):
    print('Sandwich Event: ' + data)
    emit('sandwich', data, broadcast=True)

@socketio.on('deli')
def handle_deli_event(data):
    print('Deli Event: ' + data)
    emit('deli', data, broadcast=True)

@socketio.on('disconnect')
def disconnect(data):
    print('Disconnected')

@socketio.on_error_default  # Default handler for all errors
def error_handler(e):
    print('An error has occurred:', e)


@app.route('/print', methods=['POST'])
def print_file():
    try:
        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({"code": 400, "status": "error", "msg": "No JSON data received"}), 400
        
        content = data.get('content', '')
        if not content:
            print("Received content is empty")
            return jsonify({"code": 400, "status": "error", "msg": "Received content is empty"}), 400
        else:
            print(f"Received content: '{content}'")
        
        # Replace literal \n with actual newlines
        content = content.replace('\\n', '\n')
        content = content.replace('\\$', '$')
        
        # Write the content to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Content written to {file_path}")
        
        # Check if the file exists
        if os.path.exists(file_path):
            print(f"File {file_path} exists.")
            # Read and print file content for verification
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            print(f"File content: '{file_content}'")
        else:
            print(f"File {file_path} does not exist.")
            return jsonify({"code": 500, "status": "error", "msg": f"File {file_path} does not exist."}), 500
        
        # Print the file using a PowerShell command to ensure it uses the correct printer
        print(f"Attempting to print the file {file_path} using PowerShell")
        powershell_command = f'Start-Process -FilePath notepad.exe -ArgumentList "/p {file_path}" -NoNewWindow -Wait'
        result = subprocess.run(['powershell', '-Command', powershell_command], shell=True)
        print(f"Subprocess finished with return code {result.returncode}")
        
        if result.returncode == 0:
            return jsonify({"code": 200, "status": "success", "msg": "File printed successfully"}), 200
        else:
            return jsonify({"code": 500, "status": "error", "msg": "Failed to print file"}), 500

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"code": 500, "status": "error", "msg": f"An error occurred: {e}"}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True)
