FROM python:3.10-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Dependências do sistema
RUN apt-get update \
&& apt-get install -y --no-install-recommends \
build-essential \
libpq-dev \
gettext \
git \
&& rm -rf /var/lib/apt/lists/*


WORKDIR /app


# copiar apenas requirements primeiro para aproveitar cache
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
&& pip install -r /app/requirements.txt


# copiar código da aplicação
COPY . /app


# tornar entrypoint executável
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


# diretório padrão para coletar arquivos estáticos
RUN mkdir -p /app/staticfiles /app/media


# porta padrão
EXPOSE 8000


# ponto de entrada
ENTRYPOINT ["/entrypoint.sh"]
