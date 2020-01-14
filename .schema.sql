CREATE SCHEMA clubhouse;

CREATE TABLE IF NOT EXISTS member_info (
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
  clubhouse_id        INT
);

CREATE TABLE IF NOT EXISTS checkins (
  member_id           INT,
  checkin_datetime    DATETIME,
  checkout_datetime   TIME,
  clubhouse_id        INT
);
