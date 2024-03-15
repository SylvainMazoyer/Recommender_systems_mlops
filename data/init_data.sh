#!/bin/bash

echo "Waiting for PostgreSQL to start..."
sleep 10


# PGPASSWORD=dataflix psql -h data_container -U postgres -d dataflix -c "\copy films FROM 'data/films.csv' DELIMITER ',' CSV HEADER;"
# PGPASSWORD=dataflix psql -h data_container -U postgres -d dataflix -c "\copy notes FROM 'data/notes.csv' DELIMITER ',' CSV HEADER;"
# PGPASSWORD=dataflix psql -h data_container -U postgres -d dataflix -c "\copy utilisateurs FROM 'data/utilisateurs.csv' DELIMITER ',' CSV HEADER;"

psql "postgresql://postgres:dataflix@data_container/dataflix" -c "\copy admins FROM 'data/admin.csv' DELIMITER ',' CSV HEADER;"
psql "postgresql://postgres:dataflix@data_container/dataflix" -c "SELECT SETVAL('admins_admin_id_seq', max(admin_id), TRUE) FROM admins;"

psql "postgresql://postgres:dataflix@data_container/dataflix" -c "\copy films FROM 'data/films.csv' DELIMITER ',' CSV HEADER;"
psql "postgresql://postgres:dataflix@data_container/dataflix" -c "SELECT SETVAL('films_movieid_seq', max(movieId), TRUE) FROM films;"

psql "postgresql://postgres:dataflix@data_container/dataflix" -c "\copy notes FROM 'data/notes.csv' DELIMITER ',' CSV HEADER;"
psql "postgresql://postgres:dataflix@data_container/dataflix" -c "SELECT SETVAL('notes_ratingid_seq', max(ratingId), TRUE) FROM notes;"

psql "postgresql://postgres:dataflix@data_container/dataflix" -c "\copy utilisateurs FROM 'data/utilisateurs.csv' DELIMITER ',' CSV HEADER;"
psql "postgresql://postgres:dataflix@data_container/dataflix" -c "SELECT SETVAL('utilisateurs_userid_seq', max(userId), TRUE) FROM utilisateurs;"