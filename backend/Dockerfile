FROM python:3.7-slim
WORKDIR /app
COPY ./backend/ .
RUN pip install -r requirements.txt
CMD ["gunicorn", "runserver", "--noreload", "0.0.0.0:8000"]