from flask import Flask, request, jsonify
import subprocess
import os
from flask_cors import CORS
CORS(app)

app = Flask(__name__)

printer_name = "EPSON TM-T88V Receipt"
file_path = r"c:\users\kiosk-1\desktop\printfile.txt"

@app.route('/print', methods=['POST'])
def print_file():
    try:
        data = request.get_json()
        if not data:
            print("No JSON data received")
            return "No JSON data received", 400

        content = data.get('content', '')
        
        if not content:
            print("Received content is empty")
            return "Received content is empty", 400
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
            return f"File {file_path} does not exist.", 500
        
        # Print the file using a PowerShell command to ensure it uses the correct printera
        print(f"Attempting to print the file {file_path} using PowerShell")
        powershell_command = f'Start-Process -FilePath notepad.exe -ArgumentList "/p {file_path}" -NoNewWindow -Wait'
        result = subprocess.run(['powershell', '-Command', powershell_command], shell=True)
        print(f"Subprocess finished with return code {result.returncode}")
        
        return 'File printed successfully', 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
