Here is the complete and structured re-write of your **Linux Server Health Monitoring and Analysis System** architecture, with file names, Flask apps using separate port numbers, and explanations for each component.

---

### 1. **Introduction of the Architecture**

In the **Linux Server Health Monitoring and Analysis System**, data collection and machine learning analysis are separated into different components to ensure scalability and security. 

The architecture involves three main components:
- **Metrics Collector**: Runs on the Linux server being monitored. It collects system metrics and sends them to the **Analysis Server**.
- **Analysis Server**: Receives data, analyzes it using a pre-trained TensorFlow model, and stores the results in an SQLite3 database.
- **Web Console**: Provides a user interface to view and manage historical analysis data stored on the **Analysis Server**.

This architecture allows the Linux server to focus solely on metrics collection while all machine learning and data processing tasks are handled centrally by the **Analysis Server**.

---

### 2. **Metrics Collector**

The **Metrics Collector** is responsible for gathering system metrics such as CPU usage, memory usage, disk space, swap usage, and kernel parameters. These metrics are sent via HTTP to the **Analysis Server** for processing.

#### Python Code for Metrics Collector

**File Name:** `metrics_collector.py`  
**Location:** `/path/to/metrics_collector/metrics_collector.py`

```python
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
    result = subprocess.run(['top', '-bn1'], capture_output=True, shell=True, text=True).stdout
    cpu_info = [line for line in result.splitlines() if "Cpu(s)" in line]
    idle_percentage = float(cpu_info[0].split()[7].replace('%id,', ''))
    cpu_usage = 100.0 - idle_percentage
    return cpu_usage77

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

# Collect and send data to analysis server
def collect_and_send_data():
    data = {
        'total_memory': get_memory_usage()[0],
        'used_memory': get_memory_usage()[1],
        'cpu_usage': get_cpu_usage(),
        'total_disk': get_disk_usage()[0],
        'used_disk': get_disk_usage()[1],
        'total_swap': get_swap_usage()[0],
        'used_swap': get_swap_usage()[1],
        'kernel_params': get_kernel_parameters()
    }

    response = requests.post('http://<ANALYSIS_SERVER_IP>:5000/analyze', json=data)
    if response.status_code == 200:
        print("Data successfully sent for analysis")
    else:
        print("Failed to send data")

# Run the collector
collect_and_send_data()
```

This code collects the necessary metrics from the Linux server and sends them to the **Analysis Server** at port `5000`.

---

### 3. **Analysis Server Overview**

The **Analysis Server** is the central processing hub. It receives system metrics from the **Metrics Collector**, performs machine learning analysis using a pre-trained **TensorFlow** model, and stores the results in an **SQLite3** database for historical analysis. 

This server is responsible for providing tuning recommendations, such as kernel adjustments, resource upgrades, or leaving the system unchanged.

---

### 4. **Web Console Overview**

The **Web Console** runs on the **Analysis Server** and provides an interface for users to interact with the stored data. Built using **Flask-Admin with AdminLTE**, the console allows users to:
- Start or stop metrics collection.
- View or delete historical records.
- Visualize performance recommendations and metrics.

The **Web Console** uses an **SQLite3** database to manage and store data, ensuring that users can access past performance metrics for review and comparison.

---

### 5. **System Diagram**

```plaintext
+-----------------------+         +------------------------+         +--------------------------+
| Linux Server (Metrics  |         | Analysis Server         |         | Web Console               |
| Collector)             | ----->  | (ML Model, SQLite3,     | ----->  | (Flask-Admin with         |
|                        |         | Flask Admin with        |         | AdminLTE, SQLite3)        |
+-----------------------+         +------------------------+         +--------------------------+
```

---

### 6. **Step-by-Step Code for Analysis Server with TensorFlow**

**File Name:** `analysis_server.py`  
**Location:** `/path/to/analysis_server/analysis_server.py`  
**Port:** `5000`

```python
from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import sqlite3
import json

app = Flask(__name__)

# Load pre-trained TensorFlow model
model = tf.keras.models.load_model('server_health_model.h5')

@app.route('/analyze', methods=['POST'])
def analyze_data():
    data = request.json
    
    # Convert incoming data for TensorFlow model
    input_data = np.array([
        data['total_memory'], data['used_memory'], data['cpu_usage'],
        int(data['total_disk'][:-1]), int(data['used_disk'][:-1]),
        data['total_swap'], data['used_swap'],
        data['kernel_params']['fs.file-max'],
        data['kernel_params']['net.ipv4.tcp_fin_timeout'],
        data['kernel_params']['kernel.msgmax'],
        data['kernel_params']['vm.swappiness']
    ]).reshape(1, -1)

    # Use the TensorFlow model to make predictions
    prediction = model.predict(input_data)
    predicted_class = np.argmax(prediction)
    
    # Recommendation based on prediction
    recommendations = ["No changes needed", "Increase kernel parameters", "Decrease kernel parameters", "Upgrade resources (RAM/CPU/Disk)"]
    result = {
        'predicted_class': predicted_class,
        'recommendation': recommendations[predicted_class]
    }

    # Store the result in SQLite3 database
    conn = sqlite3.connect('server_analysis.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO analysis_results (data, result) VALUES (?, ?)', (json.dumps(data), json.dumps(result)))
    conn.commit()
    conn.close()

    return jsonify(result)

# Start Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

This server listens on port `5000` and processes system metrics, returning analysis results and storing them in **SQLite3**.

---

### 7. **Flask-Admin with AdminLTE and SQLite Integration for Web Console**


### 1. **Dashboard and Menu**

In addition to the existing `Flask-Admin` interface, we will introduce a landing page (dashboard) and a side menu for easy navigation. We will use **AdminLTE** for a polished look and responsive design.

### 2. **Requirements**
Before proceeding, ensure you have the following Python packages installed:
```bash
pip install Flask Flask-SQLAlchemy Flask-Admin
```

---
**File Name:** `web_console.py`  
**Location:** `/path/to/web_console/web_console.py`  
**Port:** `5501`

```python
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server_analysis.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
admin = Admin(app, name='Server Health Monitoring', template_mode='bootstrap3')

# Models for Metrics and Analysis Results
class MetricsCollector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Integer)
    disk_usage = db.Column(db.String(50))

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Integer)
    recommendation = db.Column(db.String(200))

# Add models to Flask-Admin
admin.add_view(ModelView(MetricsCollector, db.session))
admin.add_view(ModelView(AnalysisResult, db.session))

# Dashboard Route
@app.route('/')
def dashboard():
    # Get summary data from the database
    total_metrics = MetricsCollector.query.count()
    total_analysis = AnalysisResult.query.count()
    avg_cpu_usage = db.session.query(db.func.avg(MetricsCollector.cpu_usage)).scalar()
    avg_memory_usage = db.session.query(db.func.avg(MetricsCollector.memory_usage)).scalar()

    return render_template('dashboard.html',
                           total_metrics=total_metrics,
                           total_analysis=total_analysis,
                           avg_cpu_usage=avg_cpu_usage,
                           avg_memory_usage=avg_memory_usage)

# Route for viewing filtered/sorted records
@app.route('/view_records')
def view_records():
    metrics = MetricsCollector.query.all()
    analysis_results = AnalysisResult.query.all()
    return render_template('view_records.html', metrics=metrics, analysis_results=analysis_results)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5501)

```

---

### 3. **HTML Templates for the Enhanced UI**

To create a commercial-looking landing page with **AdminLTE**, you need to create HTML templates for the dashboard and record views. 

#### Directory structure:
```
/path/to/web_console/
├── web_console.py
├── templates/
│   ├── layout.html
│   ├── dashboard.html
│   ├── view_records.html
├── static/
│   ├── css/
│   │   └── custom.css (optional for additional styling)

```

#### `layout.html` (Base Layout with Side Menu)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Server Health Monitoring</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/admin-lte/3.1.0/css/adminlte.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
</head>
<body class="hold-transition sidebar-mini layout-fixed">
<div class="wrapper">
    <!-- Navbar -->
    <nav class="main-header navbar navbar-expand navbar-white navbar-light">
        <ul class="navbar-nav">
            <li class="nav-item">
                <a class="nav-link" data-widget="pushmenu" href="#"><i class="fas fa-bars"></i></a>
            </li>
        </ul>
    </nav>

    <!-- Main Sidebar Container -->
    <aside class="main-sidebar sidebar-dark-primary elevation-4">
        <a href="/" class="brand-link">
            <span class="brand-text font-weight-light">Server Monitoring</span>
        </a>
        <div class="sidebar">
            <nav class="mt-2">
                <ul class="nav nav-pills nav-sidebar flex-column" role="menu">
                    <li class="nav-item">
                        <a href="/" class="nav-link">
                            <i class="nav-icon fas fa-tachometer-alt"></i>
                            <p>Dashboard</p>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/view_records" class="nav-link">
                            <i class="nav-icon fas fa-database"></i>
                            <p>View Records</p>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/admin" class="nav-link">
                            <i class="nav-icon fas fa-user-cog"></i>
                            <p>Admin</p>
                        </a>
                    </li>
                </ul>
            </nav>
        </div>
    </aside>

    <!-- Content Wrapper. Contains page content -->
    <div class="content-wrapper">
        <div class="content-header">
            <div class="container-fluid">
                <div class="row mb-2">
                    <div class="col-sm-6">
                        <h1 class="m-0">Server Health Monitoring</h1>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main content -->
        <div class="content">
            <div class="container-fluid">
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>

    <!-- Main Footer -->
    <footer class="main-footer text-center">
        <strong>&copy; 2024 Server Health Monitoring.</strong> All rights reserved.
    </footer>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/admin-lte/3.1.0/js/adminlte.min.js"></script>
</body>
</html>
```

---

#### `dashboard.html` (Landing Page/Dashboard)

```html
{% extends 'layout.html' %}

{% block content %}
<div class="row">
    <div class="col-lg-3 col-6">
        <div class="small-box bg-info">
            <div class="inner">
                <h3>{{ total_metrics }}</h3>
                <p>Total Metrics Collected</p>
            </div>
            <div class="icon">
                <i class="fas fa-server"></i>
            </div>
            <a href="/view_records" class="small-box-footer">More info <i class="fas fa-arrow-circle-right"></i></a>
        </div>
    </div>

    <div class="col-lg-3 col-6">
        <div class="small-box bg-success">
            <div class="inner">
                <h3>{{ avg_cpu_usage|round(2) }}%</h3>
                <p>Average CPU Usage</p>
            </div>
            <div class="icon">
                <i class="fas fa-microchip"></i>
            </div>
            <a href="/view_records" class="small-box-footer">More info <i class="fas fa-arrow-circle-right"></i></a>
        </div>
    </div>

    <div class="col-lg-3 col-6">
        <div class="small-box bg-warning">
            <div class="inner">
                <h3>{{ avg_memory_usage|round(2) }} MB</h3>
                <p>Average Memory Usage</p>
            </div>
            <div class="icon">
                <i class="fas fa-memory"></i>
            </div>
            <a href="/view_records" class="small-box-footer">More info <i class="fas fa-arrow-circle-right"></i></a>
        </div>
    </div>

    <div class="col-lg-3 col-6">
        <div class="small-box bg-danger">
            <div class="inner">
                <h3>{{ total_analysis }}</h3>
                <p>Total Analysis Performed</p>
            </div>
            <div class="icon">
                <i class="fas fa-chart-line"></i>
            </div>
            <a href="/view_records" class="small-box-footer">More info <i class="fas fa-arrow-circle-right"></i></a>
        </div>
    </div>
</div>
{% endblock %}
```

---

#### `view_records.html` (Records Overview)

```html
{% extends 'layout.html' %}

{% block content %}
<h2>Metrics and Analysis Results</h2>

<div class="row">
    <div class="col-md-12">
        <h4>Metrics</h4>
        <table class="table

 table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>CPU Usage (%)</th>
                    <th>Memory Usage (MB)</th>
                    <th>Disk Usage</th>
                </tr>
            </thead>
            <tbody>
                {% for metric in metrics %}
                <tr>
                    <td>{{ metric.id }}</td>
                    <td>{{ metric.cpu_usage }}</td>
                    <td>{{ metric.memory_usage }}</td>
                    <td>{{ metric.disk_usage }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h4>Analysis Results</h4>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>CPU Usage (%)</th>
                    <th>Memory Usage (MB)</th>
                    <th>Recommendation</th>
                </tr>
            </thead>
            <tbody>
                {% for result in analysis_results %}
                <tr>
                    <td>{{ result.id }}</td>
                    <td>{{ result.cpu_usage }}</td>
                    <td>{{ result.memory_usage }}</td>
                    <td>{{ result.recommendation }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

---

### 4. **Styling (Optional)**

If you want to add additional styles, you can place a `custom.css` file inside the `static/css/` directory and reference it in the HTML:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
```

---

### 5. **Running the App**

To run the enhanced **Web Console**:
1. Ensure you have your SQLite3 database setup and tables created.
2. Start the Flask app by running:
   ```bash
   python web_console.py
   ```
3. Access the app in your browser by visiting `http://<YOUR_SERVER_IP>:5501/`.

---

### 8. **SQLite Setup**

To set up the **SQLite3** database for storing the analysis results:

1. Open **SQLite3**:

```bash
sqlite3 server_analysis.db
```

2. Create the necessary tables:


**File Name:** `setup_sqlite_db.sh`  
**Location:** `/path/to/setup_sqlite_db.sh`  

```bash
#!/bin/bash

# Name of the SQLite database
DB_NAME="server_analysis.db"

# Check if sqlite3 is installed
if ! command -v sqlite3 &> /dev/null; then
    echo "sqlite3 is not installed. Please install it and try again."
    exit 1
fi

# Create the database and the tables
sqlite3 $DB_NAME <<EOF
CREATE TABLE IF NOT EXISTS metrics_collector (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpu_usage FLOAT,
    memory_usage INTEGER,
    disk_usage TEXT
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpu_usage FLOAT,
    memory_usage INTEGER,
    recommendation TEXT
);
EOF

# Check if the tables were created successfully
if [ $? -eq 0 ]; then
    echo "Database and tables created successfully in $DB_NAME"
else
    echo "There was an error creating the database or tables."
fi

```

---

### 9. **TensorFlow Prediction Explanation**

**TensorFlow** processes the system metrics received from the **Metrics Collector**. The metrics are passed as input to the pre-trained **TensorFlow** model, which predicts the system's health and provides recommendations such as:
- **No changes needed**.
- **Increase kernel parameters**.
- **Decrease kernel parameters**.
- **Upgrade system resources**.

The results of the prediction are stored in the **SQLite3** database for historical reference, and users can view these through the **Web Console**.

---

### Complete File Structure

```
/path/to/metrics_collector/
    ├── metrics_collector.py

/path/to/analysis_server/
    ├── analysis_server.py

/path/to/web_console/
    ├── web_console.py

```

With this structure and code, you can now implement the **Linux Server Health Monitoring and Analysis System** with clear separation of concerns between metrics collection, analysis, and the web interface for managing data.

Let me know if you need further assistance or adjustments!
