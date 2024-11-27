FROM python:3.9

RUN apt update
RUN apt install libgl1-mesa-glx libopencv-dev

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user app/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user app/ /app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]