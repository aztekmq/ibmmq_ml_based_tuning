# **IBM MQ ML-Based Tuning: Linux Server Health Monitoring and Analysis System**

## Section 1: Metrics Collector

The **Metrics Collector** section is responsible for collecting system data such as CPU, memory, disk, and kernel parameters and sending them to the **Analysis Server**.

### Relevant Files:
- **`/app/views.py`**: Contains the Flask route `/collect_metrics`, which receives system metrics via a POST request from the **Metrics Collector**.
- **`/app/templates/metrics_collector.html`**: Displays the metrics data (CPU, memory, disk usage) on the web interface.
- **`/app/models.py`**: Contains the `MetricsCollector` model, which can be used to store metrics in a database.

## Section 2: Analysis Server

The **Analysis Server** processes the collected metrics and performs machine learning analysis using TensorFlow and LLaMA models, storing the results and recommendations in a database.

### Relevant Files:
- **`/app/views.py`**: Defines the `/analysis_server` route, which displays analysis results and historical data.
- **`/app/models.py`**: Contains the `AnalysisResult` model, which stores the processed analysis results.
- **`/app/templates/analysis_server.html`**: Template that displays the analysis results and historical data on the web interface.
- **`/app/templates/improvements.html`**: Displays improvements and alerts based on analysis results.
- **`/app/db_init.py`**: Initializes the database for storing analysis results using the `create_all()` method from SQLAlchemy.

## Section 3: Web Console

The **Web Console** allows users to interact with stored data, review historical analysis results, and view system metrics through a dashboard interface.

### Relevant Files:
- **`/app/templates/base.html`**: Base layout for all web pages, including the navigation menu (Metrics Collector, Analysis Server, Improvements).
- **`/app/templates/index.html`**: The main dashboard showing metrics such as the number of monitored servers, average CPU usage, and navigation links to further information.
- **`/app/templates/improvements.html`**: Displays system improvement suggestions and alerts.
- **`/app/templates/metrics_collector.html`**: Displays current system metrics being collected by the **Metrics Collector**.

---

## Directory Structure and Files

Below is the revised directory structure based on the outlined project:

```
/home/aztekmq/python/ibmmq_ml_based_tuning/
├── app/
│   ├── __init__.py              # Initialize Flask, SQLAlchemy, Flask-Admin
│   ├── config.py                # Configuration for the Flask application
│   ├── db_init.py               # Database initialization script
│   ├── models.py                # Define database models for metrics and analysis
│   ├── views.py                 # Define routes for Metrics Collector, Analysis Server, and Improvements
│   └── templates/
│       ├── base.html            # Base layout template with sidebar and navigation
│       ├── index.html           # Main dashboard displaying server monitoring stats
│       ├── analysis_server.html # Displays analysis results and historical data
│       ├── metrics_collector.html # Displays metrics data collected from servers
│       ├── improvements.html    # Displays system improvements and alerts
├── run.py                       # Script to run the Flask application
```

### Detailed File Contents:

#### `/app/__init__.py`

This file initializes the Flask application, SQLAlchemy (for database handling), and Flask-Admin (for admin interface).

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Initialize the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server_analysis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Admin
admin = Admin(app, name='Server Health Monitoring', template_mode='bootstrap3')

# Import models after initializing db to avoid circular import issues
from app.models import MetricsCollector, AnalysisResult

# Add views to Flask-Admin
admin.add_view(ModelView(MetricsCollector, db.session, name="Metrics"))
admin.add_view(ModelView(AnalysisResult, db.session, name="Analysis Results"))

# Import the routes
from app import views
```

#### `/app/models.py`

This file defines the SQLAlchemy models for storing metrics and analysis results.

```python
from app import db

class MetricsCollector(db.Model):
    __tablename__ = 'metrics_collector'
    id = db.Column(db.Integer, primary_key=True)
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Integer)
    disk_usage = db.Column(db.String(50))
    swap_usage = db.Column(db.Integer)

    def __repr__(self):
        return f'<MetricsCollector {self.id}>'

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_result'
    id = db.Column(db.Integer, primary_key=True)
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Integer)
    recommendation = db.Column(db.String(200))

    def __repr__(self):
        return f'<AnalysisResult {self.id}>'
```

#### `/app/views.py`

This file contains the routes and logic for handling requests, receiving metrics data, displaying analysis results, and showing improvements.

```python
from app import app
from flask import render_template, jsonify, request

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/metrics_collector')
def metrics_collector():
    # Example data to display in the Metrics Collector view
    metrics = {
        'cpu_usage': 75,
        'total_memory': 16384,
        'used_memory': 8192,
        'total_disk': 500,
        'used_disk': 250,
        'total_swap': 8192,
        'used_swap': 4096,
        'kernel_params': {
            'fs.file-max': 100000,
            'net.ipv4.tcp_fin_timeout': 30,
            'kernel.msgmax': 8192,
            'vm.swappiness': 10
        }
    }
    return render_template('metrics_collector.html', **metrics)

@app.route('/analysis_server')
def analysis_server():
    analysis_result = get_last_analysis()  # Placeholder function
    historical_results = get_historical_results()  # Placeholder function
    return render_template('analysis_server.html',
                           analysis_result=analysis_result,
                           historical_results=historical_results)

@app.route('/improvements')
def improvements():
    alerts = get_alerts()  # Placeholder function
    return render_template('improvements.html', alerts=alerts)

@app.route('/collect_metrics', methods=['POST'])
def collect_data():
    data = request.get_json()
    # Process data and store it in the database (example omitted)
    return jsonify({"status": "success", "data": data}), 200
```

#### `/app/templates/*`

These templates render the HTML structure and content of the web interface.

- **`base.html`**: Base layout with the sidebar and navigation.
- **`index.html`**: Main dashboard page showing summary information.
- **`metrics_collector.html`**: Displays current metrics such as CPU, memory, disk, swap usage, and kernel parameters.
- **`analysis_server.html`**: Shows analysis results and historical recommendations.
- **`improvements.html`**: Displays system improvements based on the analysis results.

---

This structure and content now align the project setup with the outline provided in the project description, organizing the **Metrics Collector**, **Analysis Server**, and **Web Console** functionality effectively.
