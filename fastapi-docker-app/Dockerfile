# Use an official Python image as the base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy current directory contents to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install the Snowflake connector
RUN pip install snowflake-connector-python

# Copy the rest of the application code
COPY . .

# Expose port 80
EXPOSE 80

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
