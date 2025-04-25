# 2K Flash Active Context

## Current Focus
We are in Phase 2: Core Functionality of the 2K Flash rebuild project. We have completed the backend foundation and frontend implementation, and are now working on integration and testing.

1. Integrating frontend with backend
2. Testing end-to-end workflow
3. Implementing data visualization
4. Adding comprehensive testing
5. Optimizing performance

## Recent Changes
- Created the project repository
- Added the comprehensive rebuild plan document
- Established the memory bank for project documentation
- Set up the basic directory structure for both backend and frontend
- Implemented configuration management system
- Set up logging framework
- Created data fetching modules for H2H GG League API
- Implemented token management system
- Created base model classes and registry
- Implemented player statistics processor
- Created winner and score prediction models
- Set up API server with initial endpoints
- Created service layer for data, predictions, and refresh operations
- Initialized Next.js frontend project with TypeScript
- Set up Shadcn UI components
- Created API client for frontend-backend communication
- Implemented frontend pages and components
- Added data visualization components

## Next Steps

### Immediate Tasks
1. Test the integration between frontend and backend
2. Implement end-to-end workflow
3. Add comprehensive testing
4. Optimize performance
5. Improve error handling and recovery

### Short-term Goals
1. Complete the integration and enhancement phase
2. Add documentation
3. Set up deployment process
4. Implement CI/CD pipeline
5. Launch the application

## Active Decisions and Considerations

### Architecture Decisions
- Using a modular, layered architecture with clear separation of concerns
- Implementing repository pattern for data access
- Using service pattern for business logic
- Creating a model registry for versioning and selection

### Technical Decisions
- Using Flask for the backend API
- Using Next.js with Shadcn UI for the frontend
- Implementing file-based storage initially, with potential migration to a database later
- Using scikit-learn and XGBoost for prediction models

### Open Questions
1. Should we implement a database from the start or begin with file-based storage?
2. What is the best approach for token retrieval from H2H GG League?
3. How should we handle scheduled tasks for data refresh?
4. What testing framework and approach should we use?

## Current Status
- Project initialization phase
- No functional components implemented yet
- Setting up project structure and documentation

## Key Challenges
1. Implementing reliable token retrieval from H2H GG League
2. Ensuring accurate player statistics calculation
3. Creating effective prediction models
4. Designing a user-friendly frontend interface
5. Implementing proper error handling and recovery

## Recent Insights
- The H2H GG League API requires token-based authentication
- Player statistics calculation needs to account for team-specific performance
- Prediction models should consider head-to-head matchup history
- The frontend needs to provide clear visualization of prediction confidence
