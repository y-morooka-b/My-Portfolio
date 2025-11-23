# MySQL8系のイメージを指定
FROM mysql:8.4.7

# MySQLのローカルの設定ファイルをコンテナにコピー
COPY ./MySQL/my.cnf /etc/mysql/conf.d/my.cnf

CMD ["mysqld"]
