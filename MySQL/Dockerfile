# MySQL8系のイメージを指定
FROM mysql:8.4.7

# 他コンテナと足並みをそろえるため、mysqlユーザーのIDを1000に
RUN groupmod -g 1000 mysql && usermod -u 1000 -g 1000 mysql

# MySQLのローカルの設定ファイルをコンテナにコピー
COPY ./MySQL/my.cnf /etc/mysql/conf.d/my.cnf

CMD ["mysqld"]
