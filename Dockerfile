FROM python:3.12-slim

WORKDIR /workspace 

COPY ./requirements.txt ./
RUN apt-get update && apt-get install git curl python3-dev build-essential libnss3 libnspr4 libgbm1 libasound2 -y

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]