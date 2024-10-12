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