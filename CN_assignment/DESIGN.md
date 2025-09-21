# Excel Mock Interviewer - Design Document

## Overview

The Excel Mock Interviewer is a web-based application designed to conduct automated Excel technical interviews. The system provides a structured interview experience with intelligent evaluation and comprehensive feedback.

## Architecture

### Core Components

1. **Streamlit Frontend**: User interface for the interview process
2. **State Management**: Interview flow control and conversation tracking
3. **Evaluation Engine**: Advanced scoring system for candidate responses
4. **Question Bank**: Structured questions organized by difficulty and topic

### Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python with state machine pattern
- **Data Storage**: JSON files for questions and transcripts
- **Deployment**: Hugging Face Spaces (free tier)

## Interview Flow

The interview follows a structured progression through multiple phases:

1. **Greeting**: Introduction and setup
2. **Warmup**: Basic Excel concepts
3. **Core Skills**: Advanced functions and formulas
4. **Scenario-based**: Real-world problem solving
5. **Troubleshooting**: Debug and fix issues
6. **Wrapup**: Final evaluation and feedback

## Evaluation System

### Scoring Components

The evaluation system analyzes responses across four dimensions:

1. **Technical Accuracy**: Correct use of Excel terminology and concepts
2. **Completeness**: Thoroughness of the response
3. **Clarity**: Communication quality and structure
4. **Excel Knowledge**: Demonstration of Excel expertise

### Scoring Algorithm

Each response is scored on a scale of 1-10 based on:
- Use of appropriate Excel terminology
- Knowledge of functions and formulas
- Understanding of data analysis concepts
- Response structure and clarity
- Phase-specific criteria

## Question Bank Structure

Questions are organized into categories:
- **Warmup**: Basic Excel knowledge and experience
- **Core Skills**: Advanced functions (VLOOKUP, PivotTables, etc.)
- **Scenario-based**: Real-world data analysis problems
- **Troubleshooting**: Debug common Excel issues

## Implementation Details

### State Management

The application uses a finite state machine to manage interview flow:
- Tracks current phase and progress
- Manages conversation history
- Controls question sequencing
- Handles evaluation and scoring

### Response Processing

1. Candidate submits response
2. System evaluates response using scoring algorithm
3. Score is stored with question metadata
4. Next question is selected based on phase
5. Interview progresses until completion threshold

### Final Report Generation

The system generates comprehensive reports including:
- Overall performance score
- Category-specific breakdowns
- Detailed assessment and recommendations
- Next steps for improvement

## Deployment

The application is designed for easy deployment on free hosting platforms:
- Hugging Face Spaces (recommended)
- Streamlit Cloud
- Local development environment

## Future Enhancements

Potential improvements include:
- Integration with external APIs for enhanced evaluation
- Custom question bank creation
- Advanced analytics and reporting
- Multi-language support