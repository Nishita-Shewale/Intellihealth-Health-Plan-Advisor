# Use the official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependencies first (better for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the app files
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Run Streamlit when the container starts
CMD ["streamlit", "run", "streamlit.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=True"]
