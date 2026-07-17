FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /service_order_master
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0",  "--port", "8000"]