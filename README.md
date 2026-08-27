````markdown
# ShipTrack 📦

A shipment analytics dashboard that processes shipping data with PySpark, stores it in SQLite, and visualizes it through a Flask-powered web dashboard.

## Overview

ShipTrack tracks order deliveries across warehouses and carriers, flags late shipments, and surfaces key metrics like average delivery time and late rate — all through a clean, browser-based dashboard.

## Pipeline

```text
shipments.csv
      ↓
PySpark (clean + calculate delays)
      ↓
processed_shipments.csv
      ↓
SQLite
      ↓
Flask
      ↓
dashboard.html
````

## Features

* Cleans and deduplicates raw shipment data
* Calculates delivery time and days late per order
* Breaks down performance by warehouse and carrier
* Live dashboard with summary cards and comparison tables

## Tech Stack

* **PySpark** – data processing and transformation
* **SQLite** – lightweight storage for processed data
* **Flask** – backend API
* **HTML/CSS/JS** – dashboard frontend

## Project Structure

```text
ShipTrack/
│
├── data/
│   └── shipments.csv
│
├── output/
│   └── processed_shipments.csv
│
├── app.py
├── pyspark_etl.py
├── dashboard.html
└── requirements.txt
```

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR-USERNAME/shiptrack-dashboard.git
cd shiptrack-dashboard
```

### 2. Set up a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the ETL pipeline

```bash
python pyspark_etl.py
```

This reads `data/shipments.csv`, processes it, and saves the result to `output/processed_shipments.csv`.

### 5. Start the dashboard

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Dashboard Preview

The dashboard shows:

* Total orders, delivered count, late count, and late rate
* Average delivery time
* Warehouse-by-warehouse performance
* Carrier-by-carrier performance

```
```
