DROP TYPE IF EXISTS gender CASCADE;
DROP TYPE IF EXISTS status CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS news CASCADE;
DROP TABLE IF EXISTS news_views CASCADE;
DROP TABLE IF EXISTS notices CASCADE;
DROP TABLE IF EXISTS notice_views CASCADE;
DROP TABLE IF EXISTS notice_supports CASCADE;
DROP TABLE IF EXISTS polls CASCADE;
DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS feedbacks CASCADE;

CREATE TYPE gender AS ENUM ('female', 'male', 'other');
CREATE TYPE status AS ENUM ('read', 'wip', 'completed');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    password VARCHAR(50),
    date_of_birth DATE,
    gender GENDER,
    zip_code CHAR(5),
    admin BOOLEAN
);

CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    body VARCHAR(1000),
    zip_code CHAR(5),
    publish_on TIMESTAMP,
    archive_on TIMESTAMP,
    created_at TIMESTAMP,
    created_by INTEGER REFERENCES users
);

CREATE TABLE news_views (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES news,
    viewed_by INTEGER REFERENCES users
);

CREATE TABLE notices (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    body VARCHAR(1000),
    zip_code CHAR(5),
    street_address VARCHAR(100),
    status STATUS,
    created_at TIMESTAMP,
    created_by INTEGER REFERENCES users,
    viewed_by INTEGER REFERENCES users,
    supported_by INTEGER REFERENCES users
);

CREATE TABLE notice_views (
    id SERIAL PRIMARY KEY,
    notice_id INTEGER REFERENCES notices,
    viewed_by INTEGER REFERENCES users
);

CREATE TABLE notice_supports (
    id SERIAL PRIMARY KEY,
    notice_id INTEGER REFERENCES notices,
    supported_by INTEGER REFERENCES users
);

CREATE TABLE polls (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    zip_code CHAR(5),
    open_on TIMESTAMP,
    close_on TIMESTAMP,
    created_at TIMESTAMP,
    created_by INTEGER REFERENCES users
);

CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls,
    thumbs_up_by INTEGER REFERENCES users,
    thumbs_down_by INTEGER REFERENCES users
);

CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    body VARCHAR(1000),
    sent_at TIMESTAMP,
    sent_by INTEGER REFERENCES users,
    acknowledged BOOLEAN
);
