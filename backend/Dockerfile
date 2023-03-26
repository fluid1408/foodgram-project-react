FROM python:3.7-slim
COPY ./ /app
RUN pip install -r /app/requirements.txt
WORKDIR /app/foodgram-project-react/backend/
CMD python manage.py runserver --noreload 0.0.0.0:8000