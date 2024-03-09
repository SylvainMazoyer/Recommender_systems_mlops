#!/bin/bash

echo "Waiting for PostgreSQL to start..."
sleep 10


# PGPASSWORD=dataflix psql -h data_container -U postgres -d dataflix -c "\copy films FROM 'data/films.csv' DELIMITER ',' CSV HEADER;"
# PGPASSWORD=dataflix psql -h data_container -U postgres -d dataflix -c "\copy notes FROM 'data/notes.csv' DELIMITER ',' CSV HEADER;"
# PGPASSWORD=dataflix psql -h data_container -U postgres -d dataflix -c "\copy utilisateurs FROM 'data/utilisateurs.csv' DELIMITER ',' CSV HEADER;"

psql "postgresql://postgres:dataflix@data_container/dataflix" -c "\copy films FROM 'data/films.csv' DELIMITER ',' CSV HEADER;"
psql "postgresql://postgres:dataflix@data_container/dataflix" -c "\copy notes FROM 'data/notes.csv' DELIMITER ',' CSV HEADER;"
psql "postgresql://postgres:dataflix@data_container/dataflix" -c "\copy utilisateurs FROM 'data/utilisateurs.csv' DELIMITER ',' CSV HEADER;"