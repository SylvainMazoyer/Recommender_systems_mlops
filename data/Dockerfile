FROM postgres:14.5

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD dataflix
ENV POSTGRES_DB dataflix

ADD films.csv /data/films.csv
ADD utilisateurs.csv /data/utilisateurs.csv
ADD notes.csv /data/notes.csv
ADD init_data.sh init_data.sh
ADD init.sql init.sql

EXPOSE 5432

RUN chmod +x /init_data.sh && \
    cp init.sql /docker-entrypoint-initdb.d/


