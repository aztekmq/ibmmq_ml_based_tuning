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