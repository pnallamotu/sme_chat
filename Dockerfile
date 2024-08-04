# Use the official Python 3.11 image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Set environment variables (replace with your actual values)
ENV env="PROD"
ENV project="pnallamotu-test"
ENV project_number="969241382112"
ENV api_key="AIzaSyBhI89IXRqDfW9pVkrwkFUadEAMpgyD4B8"
ENV region="us-central1"
ENV es_search_location="global"
ENV es_search_data_store_id="albertsons_1721868232446"
ENV es_search_serving_config_id="default_search:search"
ENV vector_search_id="6596801485818822656"
ENV vector_search_endpoint_name="sme_queries"
ENV recipes_datastore_id="sme-saved-recipes"
ENV images_bucket="albertsons-sme-images"


# Expose the port your FastAPI app runs on (typically 8000)
EXPOSE 8080

# Run your FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
