FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y libopencv-dev

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user app/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user app/ /app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]