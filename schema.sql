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
    dob DATE NOT NULL,
    hometown varchar(225),
    score INTEGER NOT NULL,
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);
CREATE TABLE FriendsWith (
	user_id int NOT NULL,
	friend_id int NOT NULL,
	FOREIGN KEY (user_id) REFERENCES Users(user_id),
	FOREIGN KEY (friend_id) REFERENCES Users(user_id),
    CONSTRAINT FriendsWith_pk PRIMARY KEY (user_id, friend_id),
    CHECK (user_id != friend_id)
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


