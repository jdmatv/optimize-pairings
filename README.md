# Election Observer Deployer: Web-Based Pairing Optimizer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.9-brightgreen.svg)](https://www.python.org/)
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)

This repository contains a containerized web application that provides a user-friendly interface for a powerful combinatorial optimization tool. It is designed to create optimal two-person pairings for observers in international election observation missions. The application takes a roster of observers and generates balanced and effective teams based on a multi-criteria scoring function, aiming to maximize overall mission effectiveness and diversity.

## Overview

This tool automates the complex logistical challenge of pairing observers by wrapping a sophisticated optimization algorithm in a simple web interface. A deployment manager can upload a master list of observers (in Excel format), configure pairing priorities through a web form, and receive a complete deployment plan.

The core of the project is a permutation-based algorithm that uses a divide-and-conquer strategy to make the computationally intensive matching process feasible for large observer rosters. The entire application is containerized with Docker for easy and consistent deployment.

## Key Features

-   **Web-Based Interface**: An intuitive HTML form allows users to upload files, set optimization weights, and configure deployment parameters without touching any code.
-   **Containerized Deployment**: Packaged with Docker for simple, one-command setup and portability across different environments.
-   **Multi-Criteria Optimization**: Generates pairings using a weighted compatibility score that balances experience, nationality diversity, and other factors.
-   **Data-Driven Feature Engineering**: Ingests raw observer data and automatically calculates detailed experience scores based on mission history and organization type.
-   **Constraint Handling**: Explicitly filters out impossible or undesirable pairings, such as two observers sharing a citizenship.
-   **Heuristic Grouping Algorithm**: Employs a divide-and-conquer strategy by grouping observers based on experience, making the combinatorial problem tractable for large rosters.

## How the Algorithm Works

1.  **Data Ingestion & Preprocessing (`library/lib5.py`)**: The application reads the uploaded master observer Excel file, cleans the data (names, nationalities), and engineers key features for each observer, most notably a weighted experience score.
2.  **Runtime Prediction (`library/lib2.py`)**: Before the full computation, the algorithm can estimate the time required by running benchmarks on smaller data subsets and extrapolating the results.
3.  **Grouping and Pairing (`library/lib3.py`)**:
    -   **Divide and Conquer**: Observers are sorted by experience and split into smaller groups (e.g., the 8 most experienced with the 8 least experienced).
    -   **Permutation & Scoring**: Within each group, the algorithm generates all possible valid pairings and evaluates each complete set against the multi-criteria compatibility score.
    -   **Optimal Selection**: For each group, the set of pairings with the highest score is chosen.
4.  **Re-balancing (`library/lib1.py`)**: An optional heuristic step can swap individuals between optimized groups to further improve the global gender balance across the entire mission.
5.  **Regional Distribution (`library/lib6.py`)**: If a regional deployment plan is provided, the algorithm distributes the optimized teams across regions, aiming for an even spread of nationalities and experience.
6.  **Output**: The final list of pairs is compiled into a deployment plan and presented to the user as either an HTML table or a downloadable Excel file.

## Getting Started with Docker

The easiest way to run the STO Deployer is with Docker.

### Prerequisites

-   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Deployment

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/jdmatv/jdmatv-optimize-pairings.git](https://github.com/jdmatv/jdmatv-optimize-pairings.git)
    cd jdmatv-optimize-pairings
    ```

2.  **Build the Docker image:**
    From the root directory of the project, run the build command. This will create a container image named `sto-deployer`.
    ```bash
    docker build -t sto-deployer .
    ```

3.  **Run the Docker container:**
    This command starts the application and maps port 8080 from the container to port 8080 on your local machine.
    ```bash
    docker run -d -p 8080:8080 --name sto-deployer-app sto-deployer
    ```

4.  **Access the Application:**
    Open your web browser and navigate to: **`http://localhost:8080/home`**

## Usage Guide

1.  Navigate to the application's home page in your browser.
2.  Enter the security PIN to access the form.
3.  Use the "Choose File" button to upload the Master STO List (`.xlsx` format).
4.  Configure the optimization priorities using the radio buttons and dropdown menus (e.g., set the importance of gender diversity, experience, and age).
5.  (Optional) Define a regional deployment by specifying the number of regions and the number of teams assigned to each.
6.  Select your preferred output format (Excel file or HTML table).
7.  Click **Submit**. The backend will perform the optimization, which may take several minutes depending on the number of observers and the complexity settings.
8.  Once complete, the results will be displayed in the browser or downloaded as an Excel file.

## Application Architecture

-   **Backend**: A high-performance web service built with **FastAPI**.
-   **Frontend**: A simple HTML form served via **Jinja2** templates.
-   **Core Logic**: A modular `library` of Python scripts handling all data processing and optimization.
-   **Server**: The application is served using **Uvicorn**, an ASGI server.
-   **Deployment**: The entire application is packaged into a **Docker** container for portability and ease of use.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
