\c dataflix;

CREATE TABLE films (
    movieId SERIAL PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL,
    genres VARCHAR(100) NOT NULL,
    youtubeId VARCHAR(100)
);
\copy films FROM 'data/films.csv' DELIMITER ',' CSV HEADER;
SELECT SETVAL('films_movieid_seq', max(movieId), TRUE) FROM films;

CREATE TABLE utilisateurs (
    userId SERIAL PRIMARY KEY,
    name_user VARCHAR(100) UNIQUE NOT NULL,
    last_viewed INTEGER 
);
\copy utilisateurs FROM 'data/utilisateurs.csv' DELIMITER ',' CSV HEADER;
SELECT SETVAL('utilisateurs_userid_seq', max(userId), TRUE) FROM utilisateurs;

CREATE TABLE notes (
    ratingId SERIAL PRIMARY KEY,
    userId INTEGER NOT NULL,
    movieId INTEGER NOT NULL,
    rating FLOAT,
    timestamp_ INTEGER
);
\copy notes FROM 'data/notes.csv' DELIMITER ',' CSV HEADER;
SELECT SETVAL('notes_ratingid_seq', max(ratingId), TRUE) FROM notes;

CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    admin_name VARCHAR(20) NOT NULL,
    admin_password VARCHAR(200) NOT NULL,
    admin_role VARCHAR(20) NOT NULL
);
\copy admins FROM 'data/admin.csv' DELIMITER ',' CSV HEADER;
SELECT SETVAL('admins_admin_id_seq', max(admin_id), TRUE) FROM admins;

