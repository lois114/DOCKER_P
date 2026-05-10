# DevOps Project — Monitoring & CI/CD

![CI](https://github.com/lois114/DOCKER-PROJET/actions/workflows/ci.yml/badge.svg)

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
git clone https://github.com/lois114/DOCKER-PROJET.git
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

Panels disponibles :
- **Requests / sec** — taux de requêtes par endpoint
- **Latence moyenne** — temps de réponse en secondes
- **Taux d'erreurs 5xx** — erreurs serveur
- **Total requêtes** — compteur global
- **Uptime App** — statut de l'application (vert = UP)

## CI/CD

Le pipeline GitHub Actions (`.github/workflows/ci.yml`) :

1. **Test** — `pytest` avec Flask test client (6 tests)
2. **Build** — `docker build` de l'image Flask
3. **Push** — push vers Docker Hub (branche `main` uniquement)

Image Docker Hub : `lois114/devops-app:latest`

### Configuration des secrets GitHub

Dans Settings > Secrets and variables > Actions :
- `DOCKERHUB_USERNAME` — ton username Docker Hub
- `DOCKERHUB_TOKEN` — token Docker Hub (Account Settings > Security > New Access Token)

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

## Architecture

```
┌─────────────┐     scrape /metrics     ┌──────────────┐
│  flask-app  │ ◄─────────────────────► │  prometheus  │
│  :5000      │                         │  :9090       │
└─────────────┘                         └──────┬───────┘
                                               │
                                        ┌──────▼───────┐
                                        │   grafana    │
                                        │   :3000      │
                                        └──────┬───────┘
                                               │
                                        ┌──────▼───────┐
                                        │ alertmanager │
                                        │   :9093      │
                                        └──────────────┘
```
