FROM python:latest
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --upgrade pip
RUN pip install flask requests
WORKDIR /usr/src/app
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]