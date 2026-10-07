# WEALTH activPAL Inference

Containerised application for processing **activPAL wearable data** using the WEALTH physical-behaviour and energy-expenditure inference pipeline.

The application packages the complete runtime environment into a **Docker container**, including the Python environment, dependencies, WEALTH package, preprocessing utilities, pretrained models, and inference code.

The application provides two complementary ways to run inference:

1. **FastAPI-based inference service** — upload an activPAL file through a REST API and download the prediction results.
2. **Batch Docker execution** — process files directly through Docker volumes without using the API.

The main objective is to provide a **reproducible, portable, and deployable way to run activPAL inference without installing the application and its dependencies directly on the host machine**.

---

## Overview

The application takes activPAL data as input, executes the WEALTH inference pipeline inside a Docker container, and generates predictions for **Physical Behaviour (PB)** and **Energy Expenditure (EE)**.

The container provides an isolated runtime environment containing:

- Python 3.12
- Required Python dependencies
- `wealth_pb_ee_models`
- Pretrained inference models
- activPAL data-processing utilities
- Inference code
- FastAPI
- Uvicorn

The host machine only needs to have **Docker** installed.

---

# Architecture

The current deployment uses **FastAPI as the inference interface**.

```text
                     Client
                       │
                       │ POST /predict
                       │ activPAL file
                       ▼
              ┌─────────────────────┐
              │      FastAPI        │
              │                     │
              │   /health           │
              │   /predict          │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ WEALTH inference    │
              │                     │
              │ Physical Behaviour  │
              │ Energy Expenditure │
              └──────────┬──────────┘
                         │
                         ▼
                 Prediction CSV
                         │
                         ▼
                    Download
```

The complete application runs inside the Docker container:

```text
┌──────────────────────────────────────────┐
│             wealth-activpal              │
│                                          │
│  Python 3.12                             │
│  FastAPI                                 │
│  Uvicorn                                 │
│  WEALTH package                          │
│  Dependencies                            │
│  Pretrained models                       │
│  Inference application                   │
│                                          │
│  /app/input                              │
│  /app/output                             │
└──────────────────────────────────────────┘
```

Input and output directories can optionally be connected to the host using Docker volume mounts.

---

# FastAPI Service

The primary deployment interface is a **FastAPI REST API**.

The API provides two endpoints:

### Health check

```text
GET /health
```

Returns:

```json
{
  "status": "ok"
}
```

This endpoint can be used to verify that the service is running.

### Prediction

```text
POST /predict
```

The endpoint accepts an activPAL file as a multipart file upload.

The processing pipeline is:

```text
activPAL file
      │
      ▼
POST /predict
      │
      ▼
Save input file
      │
      ▼
WEALTH inference
      │
      ├── Physical Behaviour
      │
      └── Energy Expenditure
      │
      ▼
Prediction DataFrame
      │
      ▼
CSV file
      │
      ▼
HTTP file download
```

The generated CSV is returned directly as a downloadable response.

---

# Interactive API Documentation

FastAPI automatically provides interactive API documentation through Swagger UI.

After starting the container, open:

```text
http://localhost:8000/docs
```

The interface allows users to:

- Inspect the available endpoints
- Upload activPAL files
- Execute predictions
- Inspect responses
- Download the generated prediction CSV

The OpenAPI specification is available at:

```text
http://localhost:8000/openapi.json
```

---

# Docker Deployment

## Requirements

The only software required on the host machine is:

- Docker

No Python installation is required on the host.

No Python packages need to be installed on the host.

---

## Build the Image

Clone the repository:

```bash
git clone https://github.com/luisfrancs/wealth_pb_ee_models.git
cd wealth_pb_ee_models
```

Build the Docker image:

```bash
docker build \
  -t wealth-activpal \
  -f deployment/activpal/Dockerfile .
```

This command:

1. Uses the specified Python base image.
2. Installs the container dependencies.
3. Copies the WEALTH package into the image.
4. Installs the package.
5. Copies the activPAL inference application.
6. Configures FastAPI/Uvicorn as the container entry point.
7. Creates the `wealth-activpal` Docker image.

The resulting image contains everything required to run the inference service.

---

# Run the FastAPI Service

Start the container with:

```bash
docker run --rm \
  -p 8000:8000 \
  wealth-activpal
```

The API will be available at:

```text
http://localhost:8000
```

Interactive documentation:

```text
http://localhost:8000/docs
```

The terminal should show:

```text
Uvicorn running on http://0.0.0.0:8000
```

---

## Port Mapping

The option:

```bash
-p 8000:8000
```

connects port `8000` on the host machine to port `8000` inside the container.

```text
Host                         Container
────────────────────────────────────────
localhost:8000  ──────────►  :8000
                              │
                              ▼
                           FastAPI
```

---

# Using the API

Open:

```text
http://localhost:8000/docs
```

Select:

```text
POST /predict
```

Then:

1. Click **Try it out**.
2. Select an activPAL `.datx` or `.csv` file.
3. Click **Execute**.
4. The WEALTH inference pipeline is executed inside the container.
5. The generated prediction CSV is returned as a downloadable file.

The API therefore provides the following workflow:

```text
activPAL DATX/CSV
       │
       ▼
    Browser
       │
       │ Upload
       ▼
    FastAPI
       │
       ▼
 WEALTH inference
       │
       ▼
 Prediction CSV
       │
       ▼
    Download
```

---

# Batch Docker Execution

The FastAPI service is the primary interface, but the container can also be used directly for batch processing.

Create input and output directories:

```bash
mkdir -p input output
```

Place the activPAL input file in the `input` directory:

```text
project/
├── input/
│   └── participant.datx
└── output/
```

Run:

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  wealth-activpal
```

This mode is useful when inference needs to be executed locally or as part of an automated batch-processing workflow.

---

# Docker Volumes

The batch-processing workflow uses Docker volume mounts:

```text
Host                    Container
────────────────────────────────────────
./input          →      /app/input
./output         ←      /app/output
```

Therefore:

```text
./input/
```

is available inside the container as:

```text
/app/input/
```

and generated predictions in:

```text
/app/output/
```

are available on the host in:

```text
./output/
```

The volume mounts are **not part of the Docker image**. They provide a connection between the running container and the host filesystem.

---

# Input

The inference pipeline currently supports activPAL data in:

- `.datx`
- `.csv`

The API accepts the file through:

```text
POST /predict
```

The batch-processing mode reads files from:

```text
/app/input
```

---

# Output

The inference pipeline generates prediction CSV files containing the WEALTH Physical Behaviour and Energy Expenditure predictions.

Example:

```text
1103-AP170004 202a 28Mar23 3-00pm for 9d_predictions.csv
```

When using the FastAPI service, the CSV is returned directly as a downloadable HTTP response.

When using batch Docker execution, the CSV is written to:

```text
/app/output
```

and can be accessed through the mounted host directory:

```text
./output/
```

---

# Container Configuration

The Docker configuration is located in:

```text
deployment/
└── activpal/
    ├── Dockerfile
    ├── requirements.txt
    ├── api.py
    └── inference.py
```

### `Dockerfile`

Defines the complete container runtime environment, including:

- Python base image
- Python dependencies
- WEALTH package installation
- Application files
- FastAPI/Uvicorn entry point

### `requirements.txt`

Contains deployment-specific Python dependencies, including the API framework and inference requirements.

### `api.py`

Implements the FastAPI application and exposes the inference functionality through HTTP endpoints.

### `inference.py`

Contains the WEALTH activPAL inference logic and provides the reusable `predict_file()` function used by the API.

The separation between `api.py` and `inference.py` allows the prediction pipeline to be used independently of the HTTP interface.

---

# Project Structure

```text
wealth_pb_ee_models/
│
├── src/
│   └── wealth_pb_ee_models/
│       └── ...                         # WEALTH Python package
│
├── deployment/
│   └── activpal/
│       ├── Dockerfile                  # Container definition
│       ├── requirements.txt            # Deployment dependencies
│       ├── api.py                      # FastAPI application
│       └── inference.py                # Inference application
│
├── notebooks/
│   └── ...                             # Development/analysis notebooks
│
├── pyproject.toml
├── README.md
└── LICENSE
```

The `deployment/activpal/` directory contains the components required to deploy the activPAL inference pipeline as a containerised service.

---

# Reproducibility

Containerisation ensures that the inference pipeline runs in a controlled software environment.

Instead of depending on the configuration of the host machine:

```text
Host Python
Host packages
Host versions
Host configuration
        │
        ▼
    Inference
```

the application uses a controlled container environment:

```text
Docker image
│
├── Python 3.12
├── Python dependencies
├── WEALTH package
├── Pretrained models
├── FastAPI
├── Uvicorn
└── Inference application
        │
        ▼
     Results
```

This reduces dependency conflicts and makes the application easier to deploy across different machines and environments.

---

# API-Based Deployment

The FastAPI implementation separates the **machine-learning inference layer** from the **user interface**.

The architecture is:

```text
              User / Application
                      │
                      │ HTTP
                      ▼
                ┌───────────┐
                │  FastAPI  │
                └─────┬─────┘
                      │
                      ▼
              WEALTH inference
                      │
              ┌───────┴───────┐
              │               │
             PB              EE
              │               │
              └───────┬───────┘
                      │
                      ▼
               Prediction CSV
```

This allows the same inference service to be used by:

- Interactive web applications
- Research interfaces
- Python clients
- Automated processing pipelines
- Other software applications
- Cloud-based services

The API therefore provides a reusable inference backend independently of the user interface.

---

# Development vs Deployment

The repository supports complementary development and deployment workflows.

## Development

The Python package can be installed locally:

```bash
pip install -e .
```

This workflow is intended for:

- Development
- Debugging
- Modifying the inference pipeline
- Experimentation
- Notebook-based analysis

## Deployment

The Docker workflow is intended for:

- Reproducible inference
- Batch processing
- API-based inference
- Deployment on different machines
- Integration into larger processing systems
- Cloud deployment

For deployment, the recommended approach is to use the Docker container rather than installing the complete Python environment manually.

---

# Relationship to the WEALTH Web Application

The FastAPI service is designed as an **inference backend**, rather than as a complete researcher-facing web application.

This allows the inference engine to remain independent from the user interface.

For example:

```text
                    WEALTH platform
                           │
             ┌─────────────┴─────────────┐
             │                           │
       Web interface                Other clients
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
                     FastAPI API
                           │
                           ▼
                  WEALTH inference
                           │
                           ▼
                     Predictions
```

A separate interactive application can therefore consume the API without containing the WEALTH model or its Python dependencies.

This separation makes the inference pipeline easier to maintain, deploy, and integrate into future applications.

---

# Future Deployment

The containerised FastAPI service provides the foundation for cloud-based deployment.

A potential production architecture is:

```text
User / Application
        │
        ▼
      HTTPS
        │
        ▼
   Cloud endpoint
        │
        ▼
   FastAPI container
        │
        ▼
 WEALTH inference
        │
        ▼
 Prediction results
```

Future development may include:

- Cloud deployment
- Model version management with MLflow
- Automated testing
- CI/CD
- Authentication and access control
- API monitoring
- Scalable inference
- Integration with larger WEALTH applications

---

# License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

# Authors

**Luis Sigcha, PhD**

---

# Citation

If you use this software in academic work, please cite both this repository and the associated WEALTH publications.

## Software Citation

```bibtex
@software{wealth_pb_ee_models,
  author  = {Sigcha, Luis},
  title   = {wealth\_pb\_ee\_models: Machine Learning Models for Physical Behaviour and Energy Expenditure Estimation},
  year    = {2026},
  url     = {https://github.com/luisfrancs/wealth_pb_ee_models}
}
```

---

## Publications

If you use this software, please cite the following publications:

1. Sigcha L, et al.  
   **Data Labelling for Free-Living Physical Activity Recognition using Thigh-Worn Wearables and Event-based Ecological Momentary Assessment.**  
   *Research Square*, 2025 (Preprint).  
   (https://www.researchsquare.com/article/rs-6835979/v1)

2. Sigcha L, et al.  
   **Robust Assessment of Free-Living Physical Behaviors and Activity Intensity Using Dual-Wearable Multitask Learning: Development and Evaluation Study From the Multicenter WEALTH Project.**  
   *JMIR mHealth and uHealth*. 2026;14:e94302.  
   https://doi.org/10.2196/94302

3. Hayes G, et al.  
   **Standardized Methods for Evaluating Physical and Eating Behaviors: The WEALTH Cross-Sectional Study Protocol.**  
   *JMIR Research Protocols*. 2026;15:e70186.  
   https://doi.org/10.2196/70186

---
