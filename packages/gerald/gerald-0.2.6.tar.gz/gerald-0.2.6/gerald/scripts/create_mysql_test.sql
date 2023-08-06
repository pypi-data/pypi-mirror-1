/*
        File    : create_mysql_test.sql
        Purpose : Create test database and user for Gerald in MySQL
        Author  : Andrew J Todd esq <andy47@halfcooked.com>
        Notes;
                - This script must be run as the 'root' MySQL user

*/

CREATE DATABASE IF NOT EXISTS gerald_test;

CREATE USER 'gerald'@'localhost' IDENTIFIED BY 'gerald';

GRANT ALL ON gerald_test.* TO 'gerald'@'localhost';
