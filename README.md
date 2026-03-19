# Wind Farm SCADA Machine Learning Analysis

## Overview

This project applies machine learning techniques to wind farm SCADA data to predict turbine power output and analyze how prediction performance is influenced by wake effects and turbine positioning.

The study combines data-driven modeling with physical interpretation of wind farm aerodynamics, providing insights into how wake interactions affect both turbine performance and model predictability.

---

## Objectives

* Develop machine learning models to predict turbine power output
* Compare linear and nonlinear modeling approaches
* Investigate wake effects using turbine spatial relationships
* Analyze how prediction accuracy varies across the wind farm
* Identify and explain challenging turbines with high prediction error

---

## Dataset

The analysis uses a DTU wind farm SCADA dataset:

* ~72,000 timestamps
* 10-minute resolution
* ~1.4 years of operation
* 42 turbines arranged in a structured grid (A–F rows, 1–7 columns)

Available signals include:

* Turbine power output
* Nacelle wind speed
* Yaw misalignment
* Mast wind speed and wind direction
* Operational status signals

> ⚠️ The dataset is not included in this repository due to size and licensing constraints.
> To run the notebook, place the dataset file in the `/data` directory.

---

## Methodology

### Feature Engineering

* Averaged mast wind speed and direction
* Circular encoding of wind direction (sin/cos)
* Lag feature: previous power output

### Models

* Linear Regression (baseline)
* Random Forest
* Gradient Boosting

### Evaluation Metrics

* Mean Absolute Error (MAE)
* Root Mean Squared Error (RMSE)

---

## Key Analysis Steps

### 1. Single Turbine Modeling

Initial models were developed for individual turbines to establish baseline performance and validate feature engineering.

### 2. Wake Chain Analysis

Turbines aligned with wind direction were analyzed (e.g. C2 → D2 → E2 → F2) to study how wake effects influence prediction accuracy.

### 3. Full Wind Farm Analysis

The pipeline was applied to all turbines, revealing spatial patterns in prediction error across the farm.

### 4. Outlier Detection

Specific turbines (e.g. E1) were identified as significantly harder to predict.

### 5. Targeted Model Tuning

Hyperparameter tuning was applied to the most difficult turbine to assess whether model improvements could reduce prediction error.

---

## Results

* Tree-based models significantly outperform linear regression
* Typical prediction error for most turbines: **RMSE ≈ 4–6 kW**
* Prediction accuracy varies spatially across the wind farm
* Turbines in stable wake conditions are easier to predict
* Turbines with complex inflow or multiple wake interactions show higher error
* Model tuning provided only modest improvement (~5%) for the most difficult turbine

---

## Key Insights

* Wind turbine power prediction is inherently nonlinear
* Wake effects influence predictability, not just performance
* Stable wake regions can improve model accuracy
* Complex flow conditions limit prediction performance regardless of model tuning
* Machine learning models are constrained by underlying physical processes

---

## Repository Structure

```text
wind-farm-scada-ml-analysis/
│
├── notebooks/
│   └── scada_wind_farm_analysis.ipynb
│
├── figures/
│   ├── spatial_rmse_map.png
│   ├── wake_chain_analysis.png
│   └── ...
│
├── data/                # (not included)
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## How to Run

1. Clone the repository:

```bash
git clone https://github.com/kacper1002/wind-farm-scada-ml-analysis.git
cd wind-farm-scada-ml-analysis
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place the dataset in the `/data` folder

4. Open and run the notebook:

```bash
notebooks/scada_wind_farm_analysis.ipynb
```

---

## Future Improvements

* Include additional physical features (e.g. turbulence intensity)
* Test advanced models (e.g. XGBoost, LightGBM)
* Incorporate temporal models (LSTM / time series approaches)
* Extend analysis to wake interaction modeling between turbines

---

## Author

Kacper Szczykno
MSc Wind Energy — Technical University of Denmark (DTU)

---

## Final Note

This project demonstrates how combining machine learning with domain knowledge can provide deeper insights into wind farm behavior, highlighting both the strengths and limitations of data-driven approaches in complex physical systems.
