CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Pictures(
    picture_id int4  AUTO_INCREMENT,
    user_id int4,
    imgdata longblob ,
    caption VARCHAR(255),
    INDEX upid_idx (user_id),
    CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
    album_id int4 NOT NULL,
    FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE
);

CREATE TABLE FriendWith(
    user_id1 int4,
    user_id2 int4,
    PRIMARY KEY (user_id1, user_id2)
    FOREIGN KEY (user_id1) REFERENCES Users(user_id),
    FOREIGN KEY (user_id2) REFERENCES Users(user_id),
    CHECK (user_id1 != user_id2)
);

CREATE TABLE Album(
    album_id int4 AUTO_INCREMENT,
    name VARCHAR(255),
    date_created DATE,
    user_id int4 NOT NULL,
    CONSTRAINT album_pk PRIMARY KEY (album_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Comment(
    comment_id int4 AUTO_INCREMENT,
    text VARCHAR(255) NOT NULL,
    comment_date DATE,
    user_id int4 NOT NULL,
    picture_id int4 NOT NULL,
    CONSTRAINT comment_pk PRIMARY KEY (comment_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Owns(
    user_id int4,
    album_id int4,
    PRIMARY KEY(user_id, album_id),
    FOREIGN KEY(user_id) REFERENCES Users(user_id),
    FOREIGN KEY (album_id) REFERENCES Album(album_id)
);

CREATE TABLE Tag(
    word VARCHAR(255) PRIMARY KEY
);

CREATE TABLE AssociatedWith(
    picture_id int4,
    word VARCHAR(255),
    PRIMARY KEY(picture_id, word),
    FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id),
    FOREIGN KEY(word) REFERENCES Tag(word)
);

CREATE TABLE Likes(
    user_id int4,
    picture_id int4,
    PRIMARY KEY(user_id, picture_id)
    FOREIGN KEY(user_id) REFERENCES Users(user_id),
    FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id)
);
INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
