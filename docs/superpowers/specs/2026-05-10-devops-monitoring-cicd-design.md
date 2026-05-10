# Projet DevOps — Monitoring & CI/CD : Design Spec

**Date :** 2026-05-10  
**Contexte :** Projet académique B3 Cybersécurité  
**Approche retenue :** Slim — docker-compose unique, stack complète, démo `docker compose up`

---

## 1. Objectif

Déployer une API REST Python Flask avec :
- Conteneurisation Docker + Docker Compose
- Pipeline CI/CD GitHub Actions (build → test → push image)
- Monitoring temps réel Prometheus + Grafana
- Alerting Alertmanager (bonus)

---

## 2. Architecture & Services

4 services orchestrés par un seul `docker-compose.yml` :

| Service | Image | Port | Rôle |
|---|---|---|---|
| `flask-app` | buildée localement | 5000 | API REST + exposition métriques Prometheus |
| `prometheus` | `prom/prometheus:latest` | 9090 | Scrape métriques toutes les 15s |
| `grafana` | `grafana/grafana:latest` | 3000 | Dashboard (admin/admin) |
| `alertmanager` | `prom/alertmanager:latest` | 9093 | Alertes critiques |

### Data flow

```
flask-app:5000/metrics  ◄──── prometheus:9090 (scrape toutes les 15s)
                                      │
                              grafana:3000 (datasource Prometheus)
                                      │
                           alertmanager:9093 (règles d'alerte)
```

---

## 3. Application Flask

### Endpoints

| Endpoint | Méthode | Réponse |
|---|---|---|
| `/health` | GET | `{"status": "ok"}` — 200 |
| `/api/data` | GET | `{"data": [...]}` — JSON fictif — 200 |
| `/metrics` | GET | Métriques Prometheus (format text) |

### Métriques exposées (via `prometheus_flask_exporter`)

- `http_requests_total` — compteur par endpoint et status code
- `http_request_duration_seconds` — histogramme de latence
- `flask_app_info` — info version app

### Fichiers

```
app/
├── app.py               # Flask app
├── requirements.txt     # flask, prometheus_flask_exporter, pytest, requests
└── Dockerfile
```

### Dockerfile

- Base image : `python:3.12-slim`
- `EXPOSE 5000`
- `CMD ["python", "app.py"]`

---

## 4. Pipeline CI/CD (GitHub Actions)

**Fichier :** `.github/workflows/ci.yml`  
**Déclencheur :** push sur toutes les branches + pull requests

### Étapes

1. **build** — `docker build` de l'image `flask-app`
2. **test** — démarrage du container + `pytest` :
   - `GET /health` → 200 OK
   - `GET /api/data` → 200 + JSON valide
   - `GET /metrics` → 200 + contient `http_requests_total`
3. **push** — `docker push` vers Docker Hub (uniquement sur branche `main`)

### Secrets GitHub requis

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

### Image publiée

`<DOCKERHUB_USERNAME>/devops-app:latest`

---

## 5. Prometheus

**Fichier :** `prometheus/prometheus.yml`

- Scrape interval : 15s
- Job `flask-app` → cible `flask-app:5000`
- Règles d'alerte chargées depuis `prometheus/alerts.yml`

---

## 6. Grafana Dashboard

Provisionné automatiquement au démarrage via `grafana/provisioning/`.

### Panels

| Panel | PromQL | Visualisation |
|---|---|---|
| Requests/sec | `rate(http_requests_total[1m])` | Time series |
| Latence moyenne | `rate(http_request_duration_seconds_sum[1m]) / rate(http_request_duration_seconds_count[1m])` | Time series |
| Taux d'erreurs 5xx | `rate(http_requests_total{status=~"5.."}[1m])` | Stat |
| Total requêtes | `sum(http_requests_total)` | Stat |
| Uptime app | `up{job="flask-app"}` | Gauge |

### Provisioning

```
grafana/provisioning/
├── datasources/prometheus.yml    # datasource Prometheus auto-configurée
└── dashboards/
    ├── dashboard.yml             # loader de dashboards
    └── app-dashboard.json        # dashboard exporté
```

---

## 7. Alertmanager (bonus)

**Règle d'alerte :** si `flask-app` est down depuis 1 minute → alerte `critical`.

```yaml
- alert: AppDown
  expr: up{job="flask-app"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "L'application Flask est down"
```

Alertes loggées dans Alertmanager — pas d'intégration email/Slack requise.

---

## 8. Structure du dépôt

```
devops-project/
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── prometheus/
│   ├── prometheus.yml
│   └── alerts.yml
├── grafana/
│   └── provisioning/
│       ├── datasources/prometheus.yml
│       └── dashboards/
│           ├── dashboard.yml
│           └── app-dashboard.json
├── alertmanager/
│   └── alertmanager.yml
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
```

---

## 9. Livrables attendus

- [ ] Code source sur GitHub (repo public)
- [ ] Pipeline CI/CD fonctionnel (badge vert sur README)
- [ ] Image Docker publiée sur Docker Hub
- [ ] Dashboard Grafana avec les 5 panels ci-dessus
- [ ] README avec instructions de déploiement (`docker compose up`)
- [ ] Alertmanager configuré (bonus)

---

## 10. Démarrage local

```bash
git clone <repo>
cd devops-project
docker compose up --build
# API      → http://localhost:5000
# Grafana  → http://localhost:3000  (admin/admin)
# Prometheus → http://localhost:9090
# Alertmanager → http://localhost:9093
```
