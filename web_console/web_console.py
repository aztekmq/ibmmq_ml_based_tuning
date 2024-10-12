from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server_analysis.db'
app.config['SECRET_KEY'] = 'your_secret_key'
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

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0

.0.0.0', port=5501)