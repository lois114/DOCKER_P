from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/data")
def data():
    return jsonify({
        "data": [
            {"id": 1, "value": "sample"},
            {"id": 2, "value": "example"},
            {"id": 3, "value": "test"}
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
