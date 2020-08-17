CREATE DATABASE IF NOT EXISTS books;

USE books;

CREATE TABLE country (
    country_id      SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    code            varchar(2),
    name            varchar (50),
    CONSTRAINT pk_country_id           PRIMARY KEY (country_id)
);

CREATE TABLE author (
    author_id       SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name            varchar(40),
    date_of_birth   DATE,
    country_id      SMALLINT UNSIGNED,
    wikipedia_url   varchar(80),
    CONSTRAINT pk_author_id            PRIMARY KEY (author_id),
    CONSTRAINT fk_country_id_author    FOREIGN KEY (country_id)      REFERENCES country (country_id)
);

CREATE TABLE series (
    series_id       SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name            varchar(50),
    CONSTRAINT pk_series_id            PRIMARY KEY (series_id)
);

CREATE TABLE publisher (
    publisher_id    SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name            varchar(30),
    founding_date   DATE,
    country_id      SMALLINT UNSIGNED,
    CONSTRAINT pk_publisher_id         PRIMARY KEY (publisher_id),
    CONSTRAINT fk_country_id_publisher FOREIGN KEY (country_id)      REFERENCES country (country_id)
);

CREATE TABLE books (
    book_id         SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    title           varchar(50),
    author_id       SMALLINT UNSIGNED,
    series_id       SMALLINT UNSIGNED,
    series_location SMALLINT UNSIGNED,
    publisher_id    SMALLINT UNSIGNED,
    release_date    DATE,
    page_count      SMALLINT UNSIGNED,
    ISBN            varchar(20),
    CONSTRAINT pk_book_id              PRIMARY KEY (book_id),
    CONSTRAINT fk_author_id_books      FOREIGN KEY (author_id)       REFERENCES author (author_id),
    CONSTRAINT fk_series_id_books      FOREIGN KEY (series_id)       REFERENCES series (series_id),
    CONSTRAINT fk_publisher_id_books   FOREIGN KEY (publisher_id)    REFERENCES publisher (publisher_id)
);

CREATE TABLE reading (
    reading_id      SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    book_id         SMALLINT UNSIGNED NOT NULL,
    start_date      DATE,
    end_date        DATE,
    CONSTRAINT pk_reading_id           PRIMARY KEY (reading_id),
    CONSTRAINT fk_book_id_reading      FOREIGN KEY (book_id)         REFERENCES books (book_id)
);