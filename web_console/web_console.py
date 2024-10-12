#!/usr/bin/python3

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server_analysis.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

# Custom Admin Index view to create a custom dashboard
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        # Fetch some summary data from the database for display
        metrics_count = MetricsCollector.query.count()
        analysis_count = AnalysisResult.query.count()
        avg_cpu_usage = db.session.query(db.func.avg(MetricsCollector.cpu_usage)).scalar() or 0
        return self.render('admin/dashboard.html',
                           metrics_count=metrics_count,
                           analysis_count=analysis_count,
                           avg_cpu_usage=avg_cpu_usage)

# Initialize Flask-Admin with custom Admin Index view
admin = Admin(app, name='Server Health Monitoring', index_view=MyAdminIndexView(), template_mode='bootstrap3')

# Add models to Flask-Admin
admin.add_view(ModelView(MetricsCollector, db.session))
admin.add_view(ModelView(AnalysisResult, db.session))

# Define a custom route for the home page
@app.route('/')
def home():
    # Redirect to the admin dashboard
    return redirect(url_for('admin.index'))

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5501)
