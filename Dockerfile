FROM python:3.11

RUN apt-get update && apt-get install -y awscli

WORKDIR /app

COPY requirements.txt .

RUN sed '/^stock-analyser-lib==.*/d' requirements.txt > filtered-requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r filtered-requirements.txt

COPY . .

CMD ["sh", "awscodeartifact.sh"]