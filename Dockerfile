FROM python:3.9

RUN useradd seattle911

WORKDIR /home/seattle911

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY static static
COPY templates templates
COPY app.py funcs.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP app.py
ENV FLASK_ENV development

RUN chown -R seattle911:seattle911 ./
USER seattle911

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]