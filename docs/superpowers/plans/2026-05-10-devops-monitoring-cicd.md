# DevOps Monitoring & CI/CD — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Déployer une API Flask avec pipeline CI/CD GitHub Actions et monitoring Prometheus + Grafana, le tout orchestré par Docker Compose.

**Architecture:** 4 services Docker (flask-app, prometheus, grafana, alertmanager) définis dans un `docker-compose.yml` unique. L'app Flask expose `/metrics` via `prometheus_flask_exporter` ; Prometheus scrape toutes les 15s ; Grafana affiche 5 panels provisionnés automatiquement.

**Tech Stack:** Python 3.12, Flask 3.0, prometheus-flask-exporter 0.23, Docker, Docker Compose v2, Prometheus, Grafana 10, Alertmanager, GitHub Actions.

---

## Structure des fichiers

```
devops-project/          ← racine du repo (C:\Users\lois1\Desktop\DEV\DOCKER)
├── app/
│   ├── app.py           ← Flask app + métriques Prometheus
│   ├── requirements.txt ← dépendances production
│   └── Dockerfile       ← image python:3.12-slim
├── tests/
│   └── test_app.py      ← tests pytest (Flask test client)
├── prometheus/
│   ├── prometheus.yml   ← scrape config + référence alertes
│   └── alerts.yml       ← règles d'alerte AppDown
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml   ← datasource auto-configurée
│       └── dashboards/
│           ├── dashboard.yml    ← loader de dashboards
│           └── app-dashboard.json ← 5 panels
├── alertmanager/
│   └── alertmanager.yml
├── docker-compose.yml
├── pytest.ini
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
```

---

## Task 1: Structure du projet + pytest.ini

**Files:**
- Create: `pytest.ini`

- [ ] **Step 1: Créer le fichier pytest.ini à la racine**

```ini
[pytest]
testpaths = tests
pythonpath = app
```

- [ ] **Step 2: Créer les dossiers nécessaires**

```bash
mkdir -p app tests prometheus grafana/provisioning/datasources grafana/provisioning/dashboards alertmanager .github/workflows
```

- [ ] **Step 3: Commit**

```bash
git add pytest.ini
git commit -m "chore: init project structure and pytest config"
```

---

## Task 2: App Flask (TDD)

**Files:**
- Create: `app/requirements.txt`
- Create: `tests/test_app.py`
- Create: `app/app.py`

- [ ] **Step 1: Créer app/requirements.txt**

```
flask==3.0.3
prometheus-flask-exporter==0.23.1
```

- [ ] **Step 2: Installer les dépendances localement**

```bash
pip install -r app/requirements.txt pytest
```

Expected: installation sans erreur

- [ ] **Step 3: Écrire les tests (fichier tests/test_app.py)**

```python
import pytest
import json


@pytest.fixture(scope="module")
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_status_code(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body(client):
    response = client.get("/health")
    data = json.loads(response.data)
    assert data["status"] == "ok"


def test_api_data_status_code(client):
    response = client.get("/api/data")
    assert response.status_code == 200


def test_api_data_has_data_key(client):
    response = client.get("/api/data")
    data = json.loads(response.data)
    assert "data" in data


def test_api_data_is_list(client):
    response = client.get("/api/data")
    data = json.loads(response.data)
    assert isinstance(data["data"], list)


def test_metrics_endpoint_accessible(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
```

- [ ] **Step 4: Vérifier que les tests échouent (app.py n'existe pas encore)**

```bash
pytest tests/ -v
```

Expected: `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 5: Créer app/app.py**

```python
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
```

- [ ] **Step 6: Lancer les tests et vérifier qu'ils passent**

```bash
pytest tests/ -v
```

Expected:
```
tests/test_app.py::test_health_status_code PASSED
tests/test_app.py::test_health_response_body PASSED
tests/test_app.py::test_api_data_status_code PASSED
tests/test_app.py::test_api_data_has_data_key PASSED
tests/test_app.py::test_api_data_is_list PASSED
tests/test_app.py::test_metrics_endpoint_accessible PASSED
6 passed
```

- [ ] **Step 7: Commit**

```bash
git add app/requirements.txt app/app.py tests/test_app.py
git commit -m "feat: add Flask app with Prometheus metrics and tests"
```

---

## Task 3: Dockerfile

**Files:**
- Create: `app/Dockerfile`

- [ ] **Step 1: Créer app/Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

- [ ] **Step 2: Builder l'image**

```bash
docker build -t devops-app ./app
```

Expected: `Successfully built <hash>` (ou `=> exporting to image`)

- [ ] **Step 3: Lancer un container de test et vérifier les endpoints**

```bash
docker run -d -p 5000:5000 --name test-flask devops-app
```

Attendre 2 secondes puis :

```bash
curl http://localhost:5000/health
```

Expected: `{"status":"ok"}`

```bash
curl http://localhost:5000/api/data
```

Expected: `{"data":[...]}`

```bash
curl -s http://localhost:5000/metrics | head -5
```

Expected: lignes commençant par `# HELP` ou `flask_http_request_total`

- [ ] **Step 4: Stopper et supprimer le container de test**

```bash
docker stop test-flask && docker rm test-flask
```

- [ ] **Step 5: Commit**

```bash
git add app/Dockerfile
git commit -m "feat: add Dockerfile for Flask app"
```

---

## Task 4: Docker Compose

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: Créer docker-compose.yml**

```yaml
services:
  flask-app:
    build: ./app
    ports:
      - "5000:5000"
    networks:
      - monitoring
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml
    networks:
      - monitoring
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
    networks:
      - monitoring
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    networks:
      - monitoring
    restart: unless-stopped

networks:
  monitoring:
    driver: bridge

volumes:
  grafana-data:
```

Note: Les fichiers de config Prometheus, Grafana et Alertmanager seront créés dans les tâches suivantes avant de lancer `docker compose up`.

- [ ] **Step 2: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add Docker Compose with all 4 services"
```

---

## Task 5: Configuration Prometheus

**Files:**
- Create: `prometheus/prometheus.yml`
- Create: `prometheus/alerts.yml`

- [ ] **Step 1: Créer prometheus/prometheus.yml**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - "alerts.yml"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "flask-app"
    static_configs:
      - targets: ["flask-app:5000"]
```

- [ ] **Step 2: Créer prometheus/alerts.yml**

```yaml
groups:
  - name: flask_app_alerts
    rules:
      - alert: AppDown
        expr: up{job="flask-app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "L'application Flask est down"
          description: "flask-app n'est plus accessible depuis plus d'1 minute."

      - alert: HighErrorRate
        expr: rate(flask_http_request_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Taux d'erreurs 5xx élevé"
          description: "Plus de 10% des requêtes retournent une erreur 5xx."
```

- [ ] **Step 3: Commit**

```bash
git add prometheus/prometheus.yml prometheus/alerts.yml
git commit -m "feat: add Prometheus scrape config and alert rules"
```

---

## Task 6: Provisioning Grafana

**Files:**
- Create: `grafana/provisioning/datasources/prometheus.yml`
- Create: `grafana/provisioning/dashboards/dashboard.yml`
- Create: `grafana/provisioning/dashboards/app-dashboard.json`

- [ ] **Step 1: Créer grafana/provisioning/datasources/prometheus.yml**

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    uid: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

- [ ] **Step 2: Créer grafana/provisioning/dashboards/dashboard.yml**

```yaml
apiVersion: 1

providers:
  - name: default
    orgId: 1
    folder: ""
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /etc/grafana/provisioning/dashboards
```

- [ ] **Step 3: Créer grafana/provisioning/dashboards/app-dashboard.json**

```json
{
  "annotations": { "list": [] },
  "description": "Flask App Monitoring Dashboard",
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": { "lineWidth": 2 }
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "id": 1,
      "options": {
        "legend": { "calcs": [], "displayMode": "list", "placement": "bottom" },
        "tooltip": { "mode": "single", "sort": "none" }
      },
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "rate(flask_http_request_total[1m])",
          "legendFormat": "{{method}} {{status}} {{path}}",
          "refId": "A"
        }
      ],
      "title": "Requests / sec",
      "type": "timeseries"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "palette-classic" },
          "custom": { "lineWidth": 2 },
          "unit": "s"
        },
        "overrides": []
      },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
      "id": 2,
      "options": {
        "legend": { "calcs": [], "displayMode": "list", "placement": "bottom" },
        "tooltip": { "mode": "single", "sort": "none" }
      },
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "rate(flask_http_request_duration_seconds_sum[1m]) / rate(flask_http_request_duration_seconds_count[1m])",
          "legendFormat": "{{path}}",
          "refId": "A"
        }
      ],
      "title": "Latence moyenne",
      "type": "timeseries"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "thresholds" },
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": null },
              { "color": "red", "value": 0.01 }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": { "h": 4, "w": 8, "x": 0, "y": 8 },
      "id": 3,
      "options": {
        "colorMode": "background",
        "graphMode": "none",
        "orientation": "auto",
        "reduceOptions": { "calcs": ["lastNotNull"], "fields": "", "values": false },
        "textMode": "auto"
      },
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "rate(flask_http_request_total{status=~\"5..\"}[1m])",
          "legendFormat": "Erreurs 5xx/s",
          "refId": "A"
        }
      ],
      "title": "Taux d'erreurs 5xx",
      "type": "stat"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "thresholds" },
          "thresholds": {
            "mode": "absolute",
            "steps": [{ "color": "blue", "value": null }]
          }
        },
        "overrides": []
      },
      "gridPos": { "h": 4, "w": 8, "x": 8, "y": 8 },
      "id": 4,
      "options": {
        "colorMode": "background",
        "graphMode": "none",
        "orientation": "auto",
        "reduceOptions": { "calcs": ["lastNotNull"], "fields": "", "values": false },
        "textMode": "auto"
      },
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "sum(flask_http_request_total)",
          "legendFormat": "Total",
          "refId": "A"
        }
      ],
      "title": "Total requêtes",
      "type": "stat"
    },
    {
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "fieldConfig": {
        "defaults": {
          "color": { "mode": "thresholds" },
          "max": 1,
          "min": 0,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "red", "value": null },
              { "color": "green", "value": 1 }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": { "h": 4, "w": 8, "x": 16, "y": 8 },
      "id": 5,
      "options": {
        "orientation": "auto",
        "reduceOptions": { "calcs": ["lastNotNull"], "fields": "", "values": false },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "targets": [
        {
          "datasource": { "type": "prometheus", "uid": "prometheus" },
          "expr": "up{job=\"flask-app\"}",
          "legendFormat": "Up",
          "refId": "A"
        }
      ],
      "title": "Uptime App",
      "type": "gauge"
    }
  ],
  "schemaVersion": 38,
  "tags": ["devops", "flask", "monitoring"],
  "title": "Flask App Dashboard",
  "uid": "flask-app-dashboard",
  "version": 1
}
```

- [ ] **Step 4: Commit**

```bash
git add grafana/
git commit -m "feat: add Grafana provisioning (datasource + 5-panel dashboard)"
```

---

## Task 7: Configuration Alertmanager

**Files:**
- Create: `alertmanager/alertmanager.yml`

- [ ] **Step 1: Créer alertmanager/alertmanager.yml**

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ["alertname"]
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: "default"

receivers:
  - name: "default"

inhibit_rules:
  - source_match:
      severity: "critical"
    target_match:
      severity: "warning"
    equal: ["alertname"]
```

- [ ] **Step 2: Lancer toute la stack et vérifier que tout démarre**

```bash
docker compose up --build -d
```

Attendre 10 secondes puis :

```bash
docker compose ps
```

Expected: les 4 services en état `Up` ou `running`

- [ ] **Step 3: Vérifier chaque service**

```bash
curl http://localhost:5000/health
```
Expected: `{"status":"ok"}`

Ouvrir `http://localhost:9090/targets` dans un navigateur — vérifier que `flask-app` est en état `UP`.

Ouvrir `http://localhost:3000` — se connecter avec `admin` / `admin` — le dashboard "Flask App Dashboard" doit apparaître dans Dashboards.

Ouvrir `http://localhost:9093` — l'interface Alertmanager doit s'afficher.

- [ ] **Step 4: Stopper la stack**

```bash
docker compose down
```

- [ ] **Step 5: Commit**

```bash
git add alertmanager/alertmanager.yml
git commit -m "feat: add Alertmanager config with AppDown and HighErrorRate rules"
```

---

## Task 8: Pipeline GitHub Actions

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Créer un repo GitHub**

Sur GitHub.com : créer un nouveau repo public nommé `devops-project`.

Ajouter les secrets dans Settings > Secrets and variables > Actions :
- `DOCKERHUB_USERNAME` — ton username Docker Hub
- `DOCKERHUB_TOKEN` — ton token Docker Hub (hub.docker.com > Account Settings > Security > New Access Token)

- [ ] **Step 2: Créer .github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: ["**"]
  pull_request:
    branches: ["**"]

jobs:
  build-test-push:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r app/requirements.txt pytest

      - name: Run tests
        run: pytest tests/ -v

      - name: Build Docker image
        run: docker build -t devops-app ./app

      - name: Login to Docker Hub
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Push to Docker Hub
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: |
          docker tag devops-app ${{ secrets.DOCKERHUB_USERNAME }}/devops-app:latest
          docker push ${{ secrets.DOCKERHUB_USERNAME }}/devops-app:latest
```

- [ ] **Step 3: Commit et push vers GitHub**

```bash
git add .github/workflows/ci.yml
git commit -m "feat: add GitHub Actions CI pipeline (test + build + push)"
git remote add origin https://github.com/<TON_USERNAME>/devops-project.git
git push -u origin main
```

Remplacer `<TON_USERNAME>` par ton username GitHub.

- [ ] **Step 4: Vérifier que le pipeline passe**

Sur GitHub > Actions > onglet `CI` : vérifier que tous les steps sont verts.

Expected : badge vert sur le workflow, image poussée sur Docker Hub.

---

## Task 9: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Créer README.md**

````markdown
# DevOps Project — Monitoring & CI/CD

![CI](https://github.com/<TON_USERNAME>/devops-project/actions/workflows/ci.yml/badge.svg)

API Flask avec pipeline CI/CD GitHub Actions et monitoring Prometheus + Grafana.

## Stack

| Composant | Technologie |
|---|---|
| API | Python Flask 3.0 |
| Conteneurisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana |
| Alerting | Alertmanager |

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et démarré

## Démarrage rapide

```bash
git clone https://github.com/<TON_USERNAME>/devops-project.git
cd devops-project
docker compose up --build -d
```

## Services

| Service | URL | Credentials |
|---|---|---|
| API Flask | http://localhost:5000 | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / admin |
| Alertmanager | http://localhost:9093 | — |

## Endpoints de l'API

| Endpoint | Méthode | Réponse |
|---|---|---|
| `/health` | GET | `{"status": "ok"}` |
| `/api/data` | GET | `{"data": [...]}` |
| `/metrics` | GET | Métriques Prometheus |

## Dashboard Grafana

Le dashboard **Flask App Dashboard** est provisionné automatiquement au démarrage.
Panels disponibles : Requests/sec, Latence moyenne, Taux d'erreurs 5xx, Total requêtes, Uptime App.

## CI/CD

Le pipeline GitHub Actions :
1. **Test** — pytest avec Flask test client
2. **Build** — `docker build`
3. **Push** — push vers Docker Hub (branche `main` uniquement)

Image Docker Hub : `<TON_USERNAME>/devops-app:latest`

## Tests locaux

```bash
pip install -r app/requirements.txt pytest
pytest tests/ -v
```

## Arrêter la stack

```bash
docker compose down
```

## Arrêter et supprimer les volumes

```bash
docker compose down -v
```
````

- [ ] **Step 2: Remplacer `<TON_USERNAME>` par ton vrai username GitHub dans README.md**

- [ ] **Step 3: Commit et push final**

```bash
git add README.md
git commit -m "docs: add README with deployment instructions"
git push origin main
```

- [ ] **Step 4: Vérification finale complète**

```bash
docker compose up --build -d
```

Vérifier :
- `curl http://localhost:5000/health` → `{"status":"ok"}`
- `http://localhost:9090/targets` → `flask-app` UP
- `http://localhost:3000` → dashboard visible avec données
- `http://localhost:9093` → Alertmanager actif
- GitHub Actions → badge vert sur README

```bash
docker compose down
```

---

## Checklist livrables

- [ ] Code source sur GitHub (repo public)
- [ ] Pipeline CI/CD : badge vert dans README
- [ ] Image Docker Hub publiée (`<USERNAME>/devops-app:latest`)
- [ ] Dashboard Grafana avec 5 panels
- [ ] README avec instructions de déploiement
- [ ] Alertmanager configuré (bonus)
