\c dataflix;

CREATE TABLE films (
    movieId SERIAL PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL,
    genre VARCHAR(100) NOT NULL,
    youtubeId VARCHAR(100) UNIQUE
);

CREATE TABLE utilisateurs (
    userId SERIAL PRIMARY KEY,
    name_user VARCHAR(100) UNIQUE NOT NULL,
    last_viewed INTEGER 
);

CREATE TABLE notes (
    ratingId SERIAL PRIMARY KEY,
    userId INTEGER NOT NULL,
    movieId INTEGER NOT NULL,
    rating FLOAT,
    timestamp_ INTEGER
);

