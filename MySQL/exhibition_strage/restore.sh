#!/bin/sh
mysql -h portfolio-db -P 3306 -u root -proot portfolio_db < /backup/sample.dump
