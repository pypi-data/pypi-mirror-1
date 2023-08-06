In order to make the relational database storage work you need to make sure
that the database configured thru the configlet for this product contains a
table like this one:

CREATE TABLE acquire(
  path varchar(200),
  link varchar(200),
  title varchar(200),
  description text,
  date datetime,
  PRIMARY KEY (link, date));
