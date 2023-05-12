FROM python:3.9

## App engine stuff
# Expose port you want your app on
EXPOSE 8501
#
RUN mkdir -p /app
WORKDIR /app
# Upgrade pip 
RUN pip install -U pip

COPY requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt

# Create a new directory for app (keep it in its own directory)
COPY . /app

# Run
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
