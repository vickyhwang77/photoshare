CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS FriendsWith CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
	firstname varchar (225),
    lastname varchar (225),
    gender varchar (225),
    dob INTEGER,
    hometown varchar(225),
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);
CREATE TABLE FriendsWith (
	user_id1 int NOT NULL,
	user_id2 int NOT NULL,
	FOREIGN KEY (user_id1) REFERENCES Users(user_id),
	FOREIGN KEY (user_id2) REFERENCES Users(user_id),
    CONSTRAINT FriendsWith_pk PRIMARY KEY (user_id1, user_id2),
    CHECK (user_id1 != user_id2)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);
INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');

