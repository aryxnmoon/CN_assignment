# Excel Mock Interviewer

A web-based application that conducts automated Excel technical interviews. The system provides structured questions, intelligent evaluation, and comprehensive feedback for candidates.

## Features

- **Structured Interview Flow**: Multi-phase interview with 18+ questions
- **Advanced Evaluation**: Four-dimensional scoring system
- **Comprehensive Feedback**: Detailed performance analysis and recommendations
- **Question Bank**: 40+ questions across 4 categories
- **Real-time Progress**: Visual progress tracking and scoring

## Quick Start

### Local Development

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/excel-mock-interviewer.git
   cd excel-mock-interviewer
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   streamlit run app.py
   ```

4. Open your browser to `http://localhost:8501`

### Docker Deployment

1. Build the image
   ```bash
   docker build -t excel-mock-interviewer .
   ```

2. Run the container
   ```bash
   docker run -p 8501:8501 excel-mock-interviewer
   ```

## Architecture

The application consists of:

- **Frontend**: Streamlit web interface
- **State Management**: Interview flow control and conversation tracking
- **Evaluation Engine**: Advanced scoring system for candidate responses
- **Question Bank**: JSON-based questions organized by category and difficulty

## Interview Process

1. **Setup**: Candidate enters name and begins interview
2. **Progression**: System asks questions across multiple phases (warmup, core skills, scenarios, troubleshooting)
3. **Evaluation**: Each response is scored across four dimensions
4. **Completion**: Comprehensive report with scores and recommendations

## Evaluation System

Responses are evaluated on:

- **Technical Accuracy**: Correct use of Excel terminology and concepts
- **Completeness**: Thoroughness of the response
- **Clarity**: Communication quality and structure
- **Excel Knowledge**: Demonstration of Excel expertise

## Project Structure

```
excel-mock-interviewer/
├── app.py                    # Main application
├── comprehensive_questions.json  # Question bank
├── requirements.txt          # Dependencies
├── Dockerfile               # Container configuration
├── DESIGN.md               # Technical design document
├── PROJECT_SUMMARY.md      # Project summary
├── DEPLOYMENT.md           # Deployment guide
└── transcripts/            # Sample interview data
```

## Deployment

The application can be deployed on:

- **Hugging Face Spaces** (recommended, free)
- **Streamlit Cloud** (free)
- **Local server** with Docker

See `DEPLOYMENT.md` for detailed instructions.

## Configuration

### Question Bank

The `comprehensive_questions.json` file contains all interview questions with metadata including:
- Question text and difficulty level
- Topic and category information
- Canonical answers and keywords

### Evaluation Settings

The evaluation system uses configurable thresholds:
- Excellent: 8.0+ score
- Good: 6.0-7.9 score
- Developing: 4.0-5.9 score
- Needs improvement: Below 4.0

## Development

### Adding Questions

1. Edit `comprehensive_questions.json`
2. Add questions with proper metadata
3. Test locally before deploying

### Modifying Evaluation

1. Update scoring logic in `app.py`
2. Adjust thresholds and weights
3. Test with sample responses

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue on GitHub.