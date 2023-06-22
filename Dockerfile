# Use a base Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the contents of the myenv directory to the image
COPY myenv /app/myenv

# Install any necessary dependencies
RUN pip install --no-cache-dir -r /app/myenv/requirements.txt

# Set the entry point or CMD to run your application
# For example, if your main application file is app.py:
CMD ["python", "/app/myenv/app.py"]
