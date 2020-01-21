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
  clubhouse_id        INT NOT NULL,
  is_checked_in       BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS checkins (
  member_id           INT NOT NULL,
  checkin_datetime    DATETIME,
  checkout_datetime   DATETIME,
  clubhouse_id        INT
);

CREATE TABLE IF NOT EXISTS clubhouses (
  clubhouse_id        INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  short_name          TINYTEXT NOT NULL,
  full_name           TINYTEXT NOT NULL,
  image               TINYTEXT
);

CREATE TABLE IF NOT EXISTS logins (
  user_id             INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username            TINYTEXT NOT NULL,
  password            VARCHAR(128),
  is_admin            BOOLEAN NOT NULL DEFAULT 0
);
