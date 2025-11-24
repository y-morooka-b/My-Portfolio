# ベースイメージの指定
FROM node:25.2.1-alpine

USER node

# 作業ディレクトリの指定
WORKDIR /home/node/app

# 先にpackage.jsonとpackage-lock.jsonをマウントさせる
COPY --chown=node ./Project/My-Portfolio-Front/package*.json /home/node/app

# モジュールのインストール
RUN npm install

CMD ["npm", "start"]
