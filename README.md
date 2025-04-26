# 2K Spark - Basketball Predictions Platform

A comprehensive platform for basketball match predictions and analytics, featuring a Flask backend API and a Next.js frontend.

## Project Overview

2K Spark is a platform that provides predictions for upcoming basketball matches in the H2H GG League. It uses machine learning models to predict match winners and scores based on historical data.

## Repository Structure

- `backend/`: Flask API server and prediction models
- `frontend/`: Next.js web application
- `models/`: Trained machine learning models
- `output/`: Data files for matches and predictions
- `logs/`: Application logs

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18.17+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the API server:
   ```bash
   python app/api.py
   ```

The backend server will run on http://localhost:5000.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

The frontend will be available at http://localhost:3000.

## Features

- **Match Predictions**: AI-powered predictions for upcoming basketball matches
- **Player Statistics**: Performance data for players in the league
- **Real-time Updates**: Refresh data to get the latest predictions
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode**: Sleek, modern dark-themed UI

## Tech Stack

### Backend
- Flask
- Python
- scikit-learn
- XGBoost
- Pandas
- NumPy

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- ShadCN UI

## Data Sources

The application uses data from the H2H GG League API to fetch match history and upcoming matches.

## License

This project is licensed under the MIT License.
