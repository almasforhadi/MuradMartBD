FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=eshop.settings

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#  Run at container start instead
CMD sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn eshop.wsgi:application --bind 0.0.0.0:8000"
