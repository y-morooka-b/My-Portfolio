# My-Portfolio

- Docker環境をここで構築する
- Docker環境で動作させたいプロジェクトは `./Project/` 直下にて管理する
	- 各プロジェクトは専用のリポジトリを用意するため、ここでは管理しない

---

## アプリケーション

- webアプリケーションのURLは下記になります
	- http://localhost:3000
	- コンテナの起動後こちらのURLに飛んでください
	ホーム画面に移動します

## プロジェクトについて
- [My-Portfolio-Front](https://github.com/y-morooka-b/My-Portfolio-Front)
	- フロントエンドのプロジェクト
- [My-Portfolio-Back](https://github.com/y-morooka-b/My-Portfolio-Back)
	- バックエンドのプロジェクト

## このブランチ(draft/exhibition)について

- このブランチは展開用のブランチです
- 常に同じデータが確認できるように、専用のDBを構築しています
	- フロントエンド・バックエンドのプロジェクトでは日付固定をしています

## バッチ `exhibition.py` について

- フロントエンド・バックエンドのプロジェクトの初期設定や、
コンテナのUP等の操作を行うバッチになります
- コマンドについては以下を参照してください
	- 初期化コマンド
		- このリポジトリをクローンした際は、こちらのコマンドを実行してください
		- DBに対してデフォルトで `(JST) 2025/12/30` 分のデータをバックアップデータから Restore します
		- ```bash
		  python3 exhibition.py init
		  ```
	- コンテナの起動コマンド
		- プロジェクトを起動する際は、こちらのコマンドを実行してください
		- ```bash
		  python3 exhibition.py run
		  ```
	- コンテナの停止コマンド
		- プロジェクトを停止する際は、こちらのコマンドを実行してください
		- ```bash
		  python3 exhibition.py stop
		  ```
	- データベースのリセットコマンド
		- テーブルデータのリセットを行います
		- 初期設定コマンドの実行直後の状態に戻します
		- ```bash
		  python3 exhibition.py reset
		  ```
