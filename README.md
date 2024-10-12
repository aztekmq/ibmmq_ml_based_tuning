Architecture Overview: Linux Server Health Monitoring and Analysis System


In this revised system, we will separate the data collection and machine learning analysis into different components, following a more scalable and secure architecture. This will allow the server under observation to only collect metrics and send them to a central server for analysis, ensuring the TensorFlow analysis is done on a separate, dedicated machine.
Components Breakdown

    Metrics Collector (Running on the Linux Server under analysis):
        Collects server metrics such as CPU, memory, disk usage, swap, and kernel parameters.
        Sends these metrics to a central Analysis Server.

    Analysis Server (TensorFlow analysis is performed here):
        Receives the data from the Metrics Collector.
        Uses a machine learning model (TensorFlow) to analyze the data and provide recommendations (e.g., kernel tuning, hardware upgrades).
        Stores analysis results in an SQLLite3 database for historical records.

    Web Console (Running on the Analysis Server):
        A dashboard built using Cube.js for visualizing historical results.
        Allows users to start/stop analysis, import metrics, and view/delete historical results.
        SQLite3 is used to store and manage historical records.

Revised Architecture Diagram:

Linux Server (Metrics Collector)
    |
    V
Analysis Server (ML Model, SQLLite3, Cube.js Web Dashboard)
    |
    V
Web Console (For starting analysis, viewing results, historical data)

Step-by-Step Explanation:
Step 1: Metrics Collector (Running on the Linux Server)

This component will collect server metrics such as CPU usage, memory usage, disk space, swap, and kernel tuning parameters. Once collected, it will send these metrics to the Analysis Server via HTTP (or an API request).

import subprocess
import requests
import json

# Function to get memory usage
def get_memory_usage():
    result = subprocess.run(['free', '-m'], capture_output=True, text=True).stdout
    lines = result.splitlines()
    memory_info = lines[1].split()
    total_memory = int(memory_info[1])
    used_memory = int(memory_info[2])
    return total_memory, used_memory

# Function to get CPU usage
def get_cpu_usage():
    result = subprocess.run(['top', '-bn1', '|', 'grep', '"Cpu(s)"'], capture_output=True, shell=True, text=True).stdout
    cpu_info = result.split()
    idle_percentage = float(cpu_info[7].replace('%id,', ''))
    cpu_usage = 100.0 - idle_percentage
    return cpu_usage

# Function to get disk usage
def get_disk_usage():
    result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True).stdout
    lines = result.splitlines()
    disk_info = lines[1].split()
    total_disk = disk_info[1]
    used_disk = disk_info[2]
    return total_disk, used_disk

# Function to get swap usage
def get_swap_usage():
    result = subprocess.run(['free', '-m'], capture_output=True, text=True).stdout
    lines = result.splitlines()
    swap_info = lines[2].split()
    total_swap = int(swap_info[1])
    used_swap = int(swap_info[2])
    return total_swap, used_swap

# Function to get kernel parameters
def get_kernel_parameters():
    kernel_params = {}
    kernel_params['fs.file-max'] = int(subprocess.run(['sysctl', '-n', 'fs.file-max'], capture_output=True, text=True).stdout)
    kernel_params['net.ipv4.tcp_fin_timeout'] = int(subprocess.run(['sysctl', '-n', 'net.ipv4.tcp_fin_timeout'], capture_output=True, text=True).stdout)
    kernel_params['kernel.msgmax'] = int(subprocess.run(['sysctl', '-n', 'kernel.msgmax'], capture_output=True, text=True).stdout)
    kernel_params['vm.swappiness'] = int(subprocess.run(['sysctl', '-n', 'vm.swappiness'], capture_output=True, text=True).stdout)
    return kernel_params

# Collect the data
def collect_data():
    total_memory, used_memory = get_memory_usage()
    cpu_usage = get_cpu_usage()
    total_disk, used_disk = get_disk_usage()
    total_swap, used_swap = get_swap_usage()
    kernel_params = get_kernel_parameters()

    data = {
        'total_memory': total_memory,
        'used_memory': used_memory,
        'cpu_usage': cpu_usage,
        'total_disk': total_disk,
        'used_disk': used_disk,
        'total_swap': total_swap,
        'used_swap': used_swap,
        'kernel_params': kernel_params
    }

    return data

# Send data to analysis server
def send_data_to_analysis_server():
    data = collect_data()
    response = requests.post('http://<ANALYSIS_SERVER_IP>/analyze', json=data)
    if response.status_code == 200:
        print("Data successfully sent for analysis")
    else:
        print("Failed to send data")

# Collect and send data
send_data_to_analysis_server()

Step 2: Analysis Server (TensorFlow + SQLLite3 + Web Console)

The Analysis Server will receive the metrics collected from the Metrics Collector, run them through a pre-trained TensorFlow model, and store the results in a SQLite3 database. It will also expose a Web Console to the user.
TensorFlow Analysis

The following code shows how to set up the TensorFlow server to receive and process the collected metrics.

from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import sqlite3

app = Flask(__name__)

# Load the pre-trained model
model = tf.keras.models.load_model('server_health_model.h5')

# Analyze incoming data and return results
@app.route('/analyze', methods=['POST'])
def analyze_data():
    data = request.json
    
    # Convert data to input for TensorFlow model
    input_data = np.array([
        data['total_memory'], data['used_memory'], data['cpu_usage'], 
        int(data['total_disk'][:-1]), int(data['used_disk'][:-1]), 
        data['total_swap'], data['used_swap'],
        data['kernel_params']['fs.file-max'],
        data['kernel_params']['net.ipv4.tcp_fin_timeout'],
        data['kernel_params']['kernel.msgmax'],
        data['kernel_params']['vm.swappiness']
    ]).reshape(1, -1)

    # Make prediction
    prediction = model.predict(input_data)
    predicted_class = np.argmax(prediction)
    
    # Create result dictionary
    recommendations = ["No changes needed", 
                       "Increase kernel parameters", 
                       "Decrease kernel parameters", 
                       "Upgrade resources (RAM/CPU/Disk)"]
    
    result = {
        'predicted_class': predicted_class,
        'recommendation': recommendations[predicted_class]
    }

    # Save results to SQLite3 database
    conn = sqlite3.connect('server_analysis.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO analysis_results (data, result) VALUES (?, ?)', 
                   (json.dumps(data), json.dumps(result)))
    conn.commit()
    conn.close()

    return jsonify(result)

# Start Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

Step 3: SQLite3 + Web Console (Cube.js)

You can use Cube.js and SQLite3 to create a simple web dashboard that shows historical data and allows you to manage analysis.

    Set up SQLite3 Database:

sqlite3 server_analysis.db
sqlite> CREATE TABLE analysis_results (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, result TEXT);

    Install Cube.js:
        You can use Cube.js for visualizing and managing the analysis results. Follow the Cube.js quickstart guide to set up your web UI.

Complete Code for Both Components:
Metrics Collector (Linux Server):

import subprocess
import requests
import json

# Function to get memory usage
def get_memory_usage():
    result = subprocess.run(['free', '-m'], capture_output=True, text=True).stdout
    lines = result.splitlines()
    memory_info = lines[1].split()
    total_memory = int(memory_info[1])
    used_memory = int(memory_info[2])
    return total_memory, used_memory

# Function to get CPU usage
def get_cpu_usage():
    result = subprocess.run(['top', '-bn1', '|', 'grep', '"Cpu(s)"'], capture_output=True, shell=True, text=True).stdout
    cpu_info = result.split()
    idle_percentage = float(cpu_info[7].replace('%id,', ''))
    cpu_usage = 100.0 - idle_percentage
    return cpu_usage

# Function to get disk usage
def get_disk_usage():
    result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True).stdout
    lines = result.splitlines()
    disk_info = lines[1].split()
    total_disk = disk_info[1]
    used_disk = disk_info[2]
    return total_disk, used_disk

# Function to get swap usage
def get_swap_usage():
    result = subprocess.run(['free', '-m'], capture_output=True, text=True).stdout
    lines = result.splitlines()
    swap_info = lines[2].split()
    total_swap =

 int(swap_info[1])
    used_swap = int(swap_info[2])
    return total_swap, used_swap

# Function to get kernel parameters
def get_kernel_parameters():
    kernel_params = {}
    kernel_params['fs.file-max'] = int(subprocess.run(['sysctl', '-n', 'fs.file-max'], capture_output=True, text=True).stdout)
    kernel_params['net.ipv4.tcp_fin_timeout'] = int(subprocess.run(['sysctl', '-n', 'net.ipv4.tcp_fin_timeout'], capture_output=True, text=True).stdout)
    kernel_params['kernel.msgmax'] = int(subprocess.run(['sysctl', '-n', 'kernel.msgmax'], capture_output=True, text=True).stdout)
    kernel_params['vm.swappiness'] = int(subprocess.run(['sysctl', '-n', 'vm.swappiness'], capture_output=True, text=True).stdout)
    return kernel_params

# Collect the data
def collect_data():
    total_memory, used_memory = get_memory_usage()
    cpu_usage = get_cpu_usage()
    total_disk, used_disk = get_disk_usage()
    total_swap, used_swap = get_swap_usage()
    kernel_params = get_kernel_parameters()

    data = {
        'total_memory': total_memory,
        'used_memory': used_memory,
        'cpu_usage': cpu_usage,
        'total_disk': total_disk,
        'used_disk': used_disk,
        'total_swap': total_swap,
        'used_swap': used_swap,
        'kernel_params': kernel_params
    }

    return data

# Send data to analysis server
def send_data_to_analysis_server():
    data = collect_data()
    response = requests.post('http://<ANALYSIS_SERVER_IP>/analyze', json=data)
    if response.status_code == 200:
        print("Data successfully sent for analysis")
    else:
        print("Failed to send data")

# Collect and send data
send_data_to_analysis_server()

Analysis Server (TensorFlow + SQLLite3):

from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import sqlite3
import json

app = Flask(__name__)

# Load the pre-trained model
model = tf.keras.models.load_model('server_health_model.h5')

# Analyze incoming data and return results
@app.route('/analyze', methods=['POST'])
def analyze_data():
    data = request.json
    
    # Convert data to input for TensorFlow model
    input_data = np.array([
        data['total_memory'], data['used_memory'], data['cpu_usage'], 
        int(data['total_disk'][:-1]), int(data['used_disk'][:-1]), 
        data['total_swap'], data['used_swap'],
        data['kernel_params']['fs.file-max'],
        data['kernel_params']['net.ipv4.tcp_fin_timeout'],
        data['kernel_params']['kernel.msgmax'],
        data['kernel_params']['vm.swappiness']
    ]).reshape(1, -1)

    # Make prediction
    prediction = model.predict(input_data)
    predicted_class = np.argmax(prediction)
    
    # Create result dictionary
    recommendations = ["No changes needed", 
                       "Increase kernel parameters", 
                       "Decrease kernel parameters", 
                       "Upgrade resources (RAM/CPU/Disk)"]
    
    result = {
        'predicted_class': predicted_class,
        'recommendation': recommendations[predicted_class]
    }

    # Save results to SQLite3 database
    conn = sqlite3.connect('server_analysis.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO analysis_results (data, result) VALUES (?, ?)', 
                   (json.dumps(data), json.dumps(result)))
    conn.commit()
    conn.close()

    return jsonify(result)

# Start Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

This architecture allows for efficient and secure health monitoring, keeping the analysis load off the monitored servers and enabling centralized management of server health through the web dashboard. Let me know if you'd like to expand on this setup further!
