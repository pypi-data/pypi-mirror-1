icNews.AcQuire is a product that installs the AcQuire content type. The
latter holds information on how to collect remote information. This
configuration information is used by the acquire script that collects the
information and stores it in an relational database. In order to use this
product Regular Expression knowledge is required.

Funcionality

    * From a URL and a regular expression can collect the information of a webpage and generate a RSS file from it.
    * cron script for Unix systems that stores content in a relational database from a RSS list.
    * inetd script for Unix systems that stores content in a relational database from the collected news.

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
