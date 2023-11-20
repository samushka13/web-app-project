CREATE TYPE gender AS ENUM ("female", "male", "other");
CREATE TYPE credentials AS VARCHAR (50);
CREATE TYPE title AS VARCHAR (100);
CREATE TYPE bodytext AS VARCHAR (1000);
CREATE TYPE zipcode AS CHAR (5);
CREATE TYPE status AS ENUM ("read", "wip", "completed");

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name CREDENTIALS UNIQUE,
    password CREDENTIALS,
    date_of_birth DATE,
    gender GENDER,
    zip_code ZIPCODE,
    admin BOOLEAN,
);

CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title TITLE,
    body BODYTEXT,
    zip_code ZIPCODE,
    publish_on DATETIME,
    archive_on DATETIME,
    created_at TIMESTAMP,
    created_by INTEGER REFERENCES users,
    views INTEGER,
);

CREATE TABLE notices (
    id SERIAL PRIMARY KEY,
    title TITLE,
    body BODYTEXT,
    zip_code ZIPCODE,
    street_address TITLE,
    status STATUS,
    created_at TIMESTAMP,
    created_by INTEGER REFERENCES users,
    viewed_by INTEGER REFERENCES users [],
    supported_by INTEGER REFERENCES users [],
);

CREATE TABLE polls (
    id SERIAL PRIMARY KEY,
    title TITLE,
    zip_code ZIPCODE,
    open_on DATETIME,
    close_on DATETIME,
    created_at TIMESTAMP,
    created_by INTEGER REFERENCES users,
    thumbs_up_by INTEGER REFERENCES users [],
    thumbs_down_by INTEGER REFERENCES users [],
);

CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    title TITLE,
    body BODYTEXT,
    sent_at TIMESTAMP,
    sent_by INTEGER REFERENCES users,
    acknowledged BOOLEAN,
);
