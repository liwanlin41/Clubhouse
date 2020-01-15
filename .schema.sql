CREATE SCHEMA IF NOT EXISTS clubhouse;

CREATE TABLE IF NOT EXISTS members (
  member_id           INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  first_name          TINYTEXT NOT NULL,
  last_name           TINYTEXT NOT NULL,
  street_address      TINYTEXT,
  city                TINYTEXT,
  state               TINYTEXT,
  zip_code            TINYTEXT,
  member_email        TINYTEXT,
  member_phone        TINYTEXT,
  join_date           DATE,
  birthday            DATE,
  school              TINYTEXT,
  gender              TINYTEXT,
  race_ethnicity      TINYTEXT,
  guardian_first_name TINYTEXT,
  guardian_last_name  TINYTEXT,
  guardian_relation   TINYTEXT,
  guardian_email      TINYTEXT,
  guardian_phone      TINYTEXT,
  clubhouse_id        INT NOT NULL
);

CREATE TABLE IF NOT EXISTS checkins (
  member_id           INT NOT NULL,
  checkin_datetime    DATETIME,
  checkout_datetime   DATETIME,
  clubhouse_id        INT
);

CREATE TABLE IF NOT EXISTS clubhouses (
  clubhouse_id        INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name                TINYTEXT NOT NULL,
  address             TINYTEXT NOT NULL,
  username            TINYTEXT NOT NULL,
  password            VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS admins (
  admin_id            INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username            TINYTEXT NOT NULL,
  password            VARCHAR(128)
);