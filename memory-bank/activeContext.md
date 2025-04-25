# 2K Flash Active Context

## Current Focus
We are in Phase 3: Model Refinement and Validation of the 2K Flash project. We have completed the backend foundation with prediction models and are now focusing on model validation, feature engineering, and documentation updates.

1. Refining prediction models with advanced validation techniques
2. Implementing feature engineering for better predictions
3. Optimizing models with Bayesian optimization
4. Ensuring proper model validation to prevent misleading results
5. Updating documentation to reflect current project state

## Recent Changes
- Implemented feature engineering module with advanced metrics (variance, momentum, recent form)
- Added cross-validation to winner prediction model for more reliable evaluation
- Implemented minimum sample size requirements to prevent overfitting
- Created model registry cleaning tool to remove problematic models
- Removed empty/unused API folder structure to streamline the codebase
- Enhanced score prediction model with feature selection and improved evaluation
- Fixed winner prediction model to prevent misleading 100% accuracy results
- Updated project documentation to reflect current state
- Implemented Bayesian optimization for both winner and score prediction models

## Next Steps

### Immediate Tasks
1. Complete frontend implementation with dark mode theme
2. Add data visualization components for prediction insights
3. Implement comprehensive testing for all components
4. Optimize UI with better spacing and alignment
5. Prepare the system for production deployment

### Short-term Goals
1. Complete the model refinement and validation phase
2. Finalize frontend implementation with proper UI design
3. Set up deployment process
4. Implement CI/CD pipeline
5. Launch the application with real data integration

## Active Decisions and Considerations

### Architecture Decisions
- Using a modular, layered architecture with clear separation of concerns
- Implementing repository pattern for data access
- Using service pattern for business logic
- Creating a model registry for versioning and selection
- Using feature engineering module for advanced feature extraction

### Technical Decisions
- Using Flask for the backend API
- Using Next.js with Shadcn UI for the frontend with dark mode theme
- Implementing file-based storage initially, with potential migration to a database later
- Using scikit-learn, XGBoost, and Bayesian optimization for prediction models
- Implementing cross-validation and feature selection for model validation
- Using minimum sample size requirements to prevent overfitting

### Resolved Questions
1. Using file-based storage for now, with plans to migrate to a database later
2. Implemented token retrieval via browser automation with Selenium
3. Using a refresh service with background thread for data updates
4. Using pytest for backend testing and React Testing Library for frontend

## Current Status
- Backend implementation complete with advanced prediction models
- Model validation and optimization implemented
- Feature engineering module created with advanced metrics
- API server implemented with all necessary endpoints
- Frontend implementation in progress
- Documentation updated to reflect current project state

## Key Challenges
1. Ensuring proper model validation without data leakage
2. Working exclusively with real data from the H2H GG League API
3. Creating a visually appealing UI with proper spacing and alignment
4. Balancing model complexity with prediction accuracy
5. Implementing comprehensive testing for all components

## Recent Insights
- Cross-validation is essential for reliable model evaluation
- Feature selection improves model performance and prevents overfitting
- Advanced metrics like variance, momentum, and recent form improve predictions
- Minimum sample size requirements are necessary to prevent misleading results
- The model registry needs regular maintenance to remove problematic models
