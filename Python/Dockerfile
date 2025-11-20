FROM python:3.13

# 作業ディレクトリの作成
RUN mkdir /mysite

# 作業ディレクトリの設定（以後の RUN は WORKDIR で実行）
WORKDIR /mysite

ADD ../Project/My-Portfolio-Back /mysite

# pipでrequirements.txtに指定されているパッケージを追加する
RUN pip install -r requirements.txt

# 起動
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
