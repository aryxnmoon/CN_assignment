# Deployment Guide

This guide covers deploying the Excel Mock Interviewer to various platforms.

## Prerequisites

- Python 3.9+ installed
- Git installed
- Account on deployment platform (Hugging Face, Streamlit Cloud, etc.)

## Quick Deploy Options

### Option 1: Hugging Face Spaces (Recommended - Free)

1. **Create a new Space**
   - Go to [Hugging Face Spaces](https://huggingface.co/new-space)
   - Choose "Streamlit" as the SDK
   - Name your space (e.g., `excel-mock-interviewer`)

2. **Upload files**
   - Clone this repository locally
   - Upload all files to your Space
   - Ensure `app.py` is in the root directory

3. **Configure the Space**
   - Add a `README.md` with your Space description
   - Set the Space to public or private as needed

4. **Deploy**
   - The Space will automatically build and deploy
   - Access your app at `https://huggingface.co/spaces/yourusername/excel-mock-interviewer`

### Option 2: Streamlit Cloud (Free)

1. **Prepare repository**
   - Push your code to GitHub
   - Ensure all files are committed

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file to `app.py`
   - Click "Deploy"

3. **Access your app**
   - Your app will be available at `https://your-app-name.streamlit.app`

### Option 3: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   streamlit run app.py
   ```

3. **Access locally**
   - Open `http://localhost:8501` in your browser

## Docker Deployment

### Build and Run Locally

1. **Build the image**
   ```bash
   docker build -t excel-mock-interviewer .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 excel-mock-interviewer
   ```

3. **Access the app**
   - Open `http://localhost:8501` in your browser

### Deploy to Cloud Platforms

#### Google Cloud Run
```bash
# Build and push to Google Container Registry
docker build -t gcr.io/your-project/excel-mock-interviewer .
docker push gcr.io/your-project/excel-mock-interviewer

# Deploy to Cloud Run
gcloud run deploy --image gcr.io/your-project/excel-mock-interviewer --platform managed
```

#### AWS ECS
```bash
# Build and push to ECR
docker build -t excel-mock-interviewer .
docker tag excel-mock-interviewer:latest your-account.dkr.ecr.region.amazonaws.com/excel-mock-interviewer:latest
docker push your-account.dkr.ecr.region.amazonaws.com/excel-mock-interviewer:latest
```

## Configuration

### Environment Variables

Create a `.env` file for local development:
```env
# Optional: Add any environment-specific configurations
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Customization

1. **Questions**: Edit `questions.json` to add/modify questions
2. **Evaluation**: Modify `evaluator.py` to adjust scoring weights
3. **UI**: Update `app.py` to change the interface
4. **Prompts**: Edit `prompts.py` to customize interviewer behavior

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python version compatibility

2. **File Not Found**
   - Verify `questions.json` exists in the root directory
   - Check file paths in the code

3. **Port Already in Use**
   - Change the port in the command: `streamlit run app.py --server.port 8502`

4. **Memory Issues**
   - Reduce the number of questions in `questions.json`
   - Optimize the evaluation logic

### Debug Mode

Run with debug information:
```bash
streamlit run app.py --logger.level debug
```

## Monitoring

### Logs
- Streamlit logs are displayed in the terminal
- For production, consider using a logging service

### Performance
- Monitor response times for evaluation
- Track memory usage for large question banks

## Security Considerations

1. **Data Privacy**
   - Interview data is stored locally in session state
   - No data is sent to external services
   - Consider data retention policies

2. **Access Control**
   - Implement authentication if needed
   - Use HTTPS in production

3. **Rate Limiting**
   - Consider implementing rate limiting for public deployments

## Production Checklist

- [ ] All dependencies installed
- [ ] Questions bank configured
- [ ] Environment variables set
- [ ] Security measures implemented
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Documentation updated

## Support

For deployment issues:
1. Check the logs for error messages
2. Verify all files are present
3. Test locally before deploying
4. Check platform-specific documentation

## Updates

To update the application:
1. Make changes to the code
2. Test locally
3. Commit and push to repository
4. Redeploy to your platform

The application will automatically restart with the new changes.
