![Fleet Cost Intelligence](https://img.shields.io/badge/FLEET%20COST%20INTELLIGENCE-1a1a1a?style=for-the-badge)

A portfolio project that combines Odoo 17 with a FastAPI machine learning service. The system tracks fleet operations for a transport company and uses simple ML models to predict maintenance needs, flag fuel expense anomalies, and identify unprofitable routes.

Data is synthetic and generated with Python Faker, using Saudi Arabia specific cities, driver names, plate formats, and SAR currency.

<br>

![Tech Stack](https://img.shields.io/badge/TECH%20STACK-2C3E50?style=for-the-badge)

![Python](https://img.shields.io/badge/PYTHON-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Odoo](https://img.shields.io/badge/ODOO%2017-714B67?style=for-the-badge&logo=odoo&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/POSTGRESQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![FastAPI](https://img.shields.io/badge/FASTAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/DOCKER-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![scikit-learn](https://img.shields.io/badge/SCIKIT%20LEARN-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![OWL.js](https://img.shields.io/badge/OWL.JS-9E4B9E?style=for-the-badge)
![JavaScript](https://img.shields.io/badge/JAVASCRIPT-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

<br>

![Overview](https://img.shields.io/badge/OVERVIEW-2C3E50?style=for-the-badge)

The project runs three services in Docker.

* An Odoo 17 module called `fleet_intelligence` that manages vehicles, trips, fuel logs, and maintenance records.
* A FastAPI service that reads the same PostgreSQL database and exposes three ML endpoints.
* An OWL.js dashboard inside Odoo that summarizes the AI outputs.

An hourly cron in Odoo calls the ML service and writes the predictions back into each record. Tree views then show colored badges so the status is easy to read at a glance.

<br>

![Features](https://img.shields.io/badge/FEATURES-2C3E50?style=for-the-badge)

* Custom Odoo module with four models: `fleet.vehicle.custom`, `fleet.trip`, `fleet.fuel.log`, and `fleet.maintenance.custom`.
* Synthetic data generator using Faker. It creates 20 vehicles, 500 trips, 1000 fuel logs, and 200 maintenance records. Roughly 10 percent of the fuel logs contain injected anomalies (over reporting, ghost fuel, inflated cost).
* Predictive maintenance using a Random Forest classifier. Each vehicle is classified as ok, due soon, or overdue based on features like odometer reading, age, and time since last service.
* Fuel expense anomaly detection using Isolation Forest, trained on features like liters, cost, price per liter, distance since last refuel, and consumption rate.
* Route profitability summary using linear regression combined with grouped statistics per route.
* Colored decorations on the vehicle and fuel log lists so problem records stand out.
* OWL.js client action dashboard shown as the module home page. It renders three KPI cards, a top 5 unprofitable routes table, and a six month fuel cost trend.

<br>

![Architecture](https://img.shields.io/badge/ARCHITECTURE-2C3E50?style=for-the-badge)

```
Odoo container (port 8069)
  Custom module: fleet_intelligence
    Models, views, hourly cron, OWL.js dashboard
  Talks to the ML service inside the Docker network

FastAPI container (port 8000)
  /predict/maintenance      Random Forest classifier
  /predict/fuel-anomaly     Isolation Forest
  /predict/route-profit     Linear Regression plus route summary

PostgreSQL container (port 5432)
  Shared by Odoo and the ML service
```

<br>

![Project Structure](https://img.shields.io/badge/PROJECT%20STRUCTURE-2C3E50?style=for-the-badge)

```
fleet_intelligence_odoo/
├── docker_compose.yml
├── odoo.conf
├── BLUEPRINT.md
├── PROJECT_TRACKING.md
├── CLAUDE_RULES.md
├── addons/
│   └── fleet_intelligence/
│       ├── __manifest__.py
│       ├── models/
│       │   ├── vehicle.py
│       │   ├── trip.py
│       │   ├── fuel_log.py
│       │   ├── maintenance.py
│       │   ├── ml_client.py
│       │   └── dashboard.py
│       ├── views/
│       │   ├── fleet_views.xml
│       │   └── dashboard_action.xml
│       ├── data/
│       │   └── ml_cron.xml
│       ├── static/src/components/
│       │   ├── dashboard.js
│       │   └── dashboard.xml
│       └── security/
│           └── ir.model.access.csv
├── ml_service/
│   ├── main.py
│   ├── db.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── models/
│       ├── maintenance_model.py
│       ├── fuel_anomaly_model.py
│       └── route_profit_model.py
└── scripts/
    └── generate_data.py
```

<br>

![Getting Started](https://img.shields.io/badge/GETTING%20STARTED-2C3E50?style=for-the-badge)

You need Docker Desktop and Python 3.11 installed.

**1. Clone and start the containers**

```bash
git clone <repo url>
cd fleet_intelligence_odoo
docker compose up -d
```

**2. Create the Odoo database**

Open http://localhost:8069 and create a database named `fleet_dev`. Set the country to Saudi Arabia.

**3. Install the module**

In Odoo, enable developer mode, then go to Apps, click Update Apps List, search for Fleet Cost Intelligence, and click Install.

**4. Generate synthetic data**

```bash
py -3.11 -m pip install Faker
py -3.11 scripts/generate_data.py
```

Update the `USERNAME` and `PASSWORD` at the top of the script if yours are different.

**5. Trigger the ML cron**

In Odoo go to Settings, Technical, Automation, Scheduled Actions. Find "Fleet Intelligence: Run ML Predictions" and click Run Manually. After it finishes, open Vehicles and Fuel Logs to see the badges.

**6. Open the dashboard**

Click Fleet Intelligence in the app switcher. The dashboard is set as the module home page.

<br>

![ML Endpoints](https://img.shields.io/badge/ML%20ENDPOINTS-2C3E50?style=for-the-badge)

The FastAPI service exposes the following endpoints. Once the containers are up, you can test them directly.

```bash
curl http://localhost:8000/predict/maintenance
curl http://localhost:8000/predict/fuel-anomaly
curl "http://localhost:8000/predict/route-profit?top_n=5"
curl "http://localhost:8000/predict/route-profit/estimate?distance_km=500"
```

Health check:

```bash
curl http://localhost:8000/health
```

<br>

![Notes](https://img.shields.io/badge/NOTES-2C3E50?style=for-the-badge)

* This is a portfolio project. The ML models are intentionally simple so the focus stays on the ERP integration and system design rather than model tuning.
* All data is synthetic. No real fleet data was used.
* The `pg_hba.conf` inside the Postgres container is set to trust for local development. Do not use this configuration in production.
* If port 5432 is already in use on your machine, stop the local Postgres service before running `docker compose up`.

<br>

![License](https://img.shields.io/badge/LICENSE-2C3E50?style=for-the-badge)

LGPL 3.0