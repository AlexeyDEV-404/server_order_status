FROM python:3.13
WORKDIR /service_order_master
COPY ./requirements.txt /service_order_master/requirements.txt
RUN pip install --no-cache-dir -r /service_order_master/requirements.txt
COPY . /service_order_master
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0",  "--port", "8000"]