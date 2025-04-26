# 2K Spark Frontend

A modern, sleek, dark-themed dashboard for basketball match predictions and analytics.

## Features

- Real-time match predictions with confidence scores
- Upcoming matches display
- Player statistics and performance metrics
- Responsive design for all screen sizes
- Dark mode by default

## Tech Stack

- Next.js 15
- React 19
- Tailwind CSS
- ShadCN UI Components
- TypeScript

## Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

### Running the Development Server

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

### Building for Production

```bash
npm run build
# or
yarn build
```

### Starting the Production Server

```bash
npm run start
# or
yarn start
```

## Backend Integration

The frontend is designed to work with the 2K Spark backend API. Make sure the backend server is running on `http://localhost:5000` before using the frontend.

To start the backend server:

```bash
cd backend
python app/api.py
```

## Project Structure

- `src/app`: Next.js app router pages
- `src/components`: React components
  - `src/components/ui`: ShadCN UI components
- `src/lib`: Utility functions and API integration

## Customization

- Theme colors can be modified in `src/app/globals.css`
- Component styling can be adjusted in the respective component files

## License

This project is licensed under the MIT License.
