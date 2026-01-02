import argparse
import os
import subprocess
from pathlib import Path
from typing import List
from urllib.parse import urlparse

# 実行するyamlの指定
COMPOSE_YAML_PATH = 'compose.exhibition.yaml'

# 作業リポジトリを入れるディレクトリ
WORK_DIR_PATH = 'Project/'

# クローンしたいリポジトリのURL一覧
REPOS = [
    'https://github.com/y-morooka-b/My-Portfolio-Front.git',
    'https://github.com/y-morooka-b/My-Portfolio-Back.git',
]

# 展開用ブランチ
EXHIBITION_BRANCH_NAME = 'draft/exhibition'


class GitManagement:
    """
    Gitリポジトリの操作（クローンやブランチのチェックアウトなど）を管理する

    このクラスは、複数のGitリポジトリを作業ディレクトリにクローンし、
    特定のブランチに切り替え、指定されたDockerディレクトリに戻るために必要な操作を処理する
    """

    _docker_dir: str
    _work_dir_list: List[str]

    def __init__(self, docker_dir: str):
        self._docker_dir = docker_dir
        self._work_dir_list = []

    def execute(self) -> None:
        self.__clones()
        self.__checkout_branches()

    def __clones(self) -> None:
        """
        複数のGitリポジトリを現在の作業用ディレクトリにクローンする。

        この関数は指定された作業ディレクトリに移動し、事前に定義されたURL一覧にある各リポジトリをクローン
        対象のディレクトリに既にリポジトリがクローンされている場合は、そのリポジトリのクローンをスキップする

        :raises FileExistsError:
            対象ディレクトリのパスが無効またはアクセスできない場合
        :raises subprocess.CalledProcessError:
            Gitコマンドの問題によりリポジトリのクローンが失敗した場合
        :raises OSError:
            ディレクトリの変更で問題が発生した場合
        """
        os.chdir(WORK_DIR_PATH)
        current_path = os.getcwd()
        print(f'作業ディレクトリ : {current_path}')

        for url in REPOS:
            repo_dir_path = os.path.join(current_path, self.__extract_repo_name(url))

            if os.path.exists(repo_dir_path):
                print(f'クローン済みのためスキップ : {repo_dir_path}')
            else:
                print(f'Cloning {url}...')
                subprocess.run(['git', 'clone', url])

            self._work_dir_list.append(repo_dir_path)

        self.__return_docker_dir()

    def __checkout_branches(self) -> None:
        """
        リモートリポジトリから最新の更新を取得し、指定したブランチに切り替える

        :param repo_dir:
            ローカルGitリポジトリのディレクトリパスを``Path``オブジェクトとして指定

        :return: None
        """

        for work_dir in self._work_dir_list:
            # git fetch でリモートブランチを取得（念のため）
            subprocess.run(['git', 'fetch'], cwd=work_dir, check=True)

            # 指定ブランチにチェックアウト
            subprocess.run(['git', 'checkout', EXHIBITION_BRANCH_NAME], cwd=work_dir, check=True)

            print(f'{work_dir} → ブランチ "{EXHIBITION_BRANCH_NAME}" にチェックアウト完了！')

    def __return_docker_dir(self) -> None:
        """
        Dockerディレクトリに移動し、現在のディレクトリのパスを表示する。
        関連するディレクトリに明示的に切り替えることで、アプリケーションがDockerコンテキスト内で動作することを保証

        :return: None
        """
        os.chdir(self._docker_dir)
        current_path = os.getcwd()
        print(f'元のディレクトリに戻る : {current_path}')

    @staticmethod
    def __extract_repo_name(url: str) -> str:
        """
        URLから取得したリポジトリ名を返す

        :param url:
            リポジトリ名を抽出するURLの文字列
        :type url: str

        :return:
            URLから抽出したリポジトリ名
        :rtype: str
        """
        path = urlparse(url).path
        repo_name = Path(path).stem
        return repo_name


class DockerManagement:
    _docker_dir: str

    def __init__(self, docker_dir: str):
        self._docker_dir = docker_dir
        os.chdir(self._docker_dir)

    def execute(self):
        self.__stop_running_containers()
        self.__compose_pull()
        self.__compose_build()
        self.__compose_up()

    def execute_init(self):
        self.__compose_pull()
        self.__compose_build()
        self.__npm_install()
        self.__db_migrate()
        self.__db_restore()

    def execute_stop(self):
        self.__stop_running_containers()

    def execute_build(self):
        self.__compose_pull()
        self.__compose_build()

    def execute_reset_db(self):
        self.__db_migrate()
        self.__db_restore()

    def __compose_pull(self) -> None:
        """
        内部のcompose機能を使用して 'compose pull' コマンドを実行

        :return: None
        """
        self.__run_compose_command(['pull'])

    def __compose_build(self) -> None:
        """
        内部のcompose機能を使用して 'compose build' コマンドを実行

        :raises RuntimeError:
            ビルドコマンドの実行に失敗した場合
        :raises OSError:
            必要なリソースへのアクセスでエラーが発生した場合
        :return: None
        """
        self.__run_compose_command(["build"], False)

    def __compose_up(self, detach: bool = True) -> None:
        """
        提供されたパラメータに基づいて `docker-compose up` コマンドを実行
        `detach` パラメータが `True` に設定されている場合、コマンドはデタッチモード(バックグラウンド)で実行

        :param detach:
            `docker-compose up` コマンドをデタッチモード (`True`) または
            フォアグラウンドモード (`False`) で実行するかを決定
        :type detach: bool
        :return: None
        """
        
        cmd = ["up"]

        if detach:
            cmd.append("-d")

        self.__run_compose_command(cmd)

    def __stop_running_containers(self) -> None:
        """
        指定ディレクトリのdocker-composeプロジェクトで、
        コンテナが起動中なら停止する。
        """
        try:
            # 起動中のコンテナがあるか確認
            result = self.__run_compose_command(['ps', '-q'])
            container_ids = result.stdout.strip().splitlines()

            if not container_ids:
                print(f'{self._docker_dir}：起動中のコンテナはありません')

            # 停止処理
            self.__run_compose_command(['down'])
            print(f'{self._docker_dir}：コンテナを停止しました')

        except subprocess.CalledProcessError as e:
            raise Exception(f'停止処理に失敗しました（{self._docker_dir}）：{e}')

    def __db_migrate(self) -> None:
        """
        Dockerコンテナ内でデータベースマイグレーションコマンドを実行する

        このメソッドはDocker Composeを利用して、portfolio-backendサービスコンテナ内で
        `manage.py migrate`コマンドを実行します。データベースマイグレーションにより、
        定義済みのDjangoマイグレーションに基づいてデータベーススキーマの変更を適用します

        :raises subprocess.SubprocessError:
            Docker Composeコマンドが失敗した場合

        :return: None
        """
        self.__run_compose_command(['run', 'portfolio-backend', 'python' , 'manage.py', 'migrate'])

    def __npm_install(self) -> None:
        """
        npm installコマンドを実行

        このメソッドは、portfolio - dbサービスのコンテナ内で
        サービス環境に必要なnpm依存関係のインストールを行います。

        :return: None
        """
        self.__run_compose_command(['run', 'portfolio-frontend', 'npm', 'install'], False)

    def __db_restore(self) -> None:
        """
        コンテナ内でスクリプトを実行してデータベースを復元
        このメソッドは、バックアップデータを復元するためにコンテナ内にある事前に定義されたコマンドとスクリプトに依存します

        :return: None
        """
        self.__run_compose_command(['run', 'portfolio-db', 'bash', '/backup/restore.sh'])

    def __run_compose_command(self, command: list[str], capture_output:bool = True):
        try:
            command = ['docker', 'compose', '-f', COMPOSE_YAML_PATH] + command

            result = subprocess.run(
                command,
                cwd=self._docker_dir,
                capture_output=capture_output,
                text=True,
                check=True,
            )

            print(f'SUCCESSFUL {" ".join(command)} 成功（{self._docker_dir}）')
            return result
        except subprocess.CalledProcessError as e:
            raise Exception(f'ERROR {" ".join(command)} 失敗（{self._docker_dir}）: {e}')

def handle_all(args) -> None:
    docker_dir = os.getcwd()
    print(f'カレントディレクトリ : {docker_dir}')

    git_manager = GitManagement(docker_dir)
    git_manager.execute()
    docker_manager = DockerManagement(docker_dir)
    docker_manager.execute()

def handle_init(args) -> None:
    docker_dir = os.getcwd()
    print(f'カレントディレクトリ : {docker_dir}')

    git_manager = GitManagement(docker_dir)
    git_manager.execute()
    docker_manager = DockerManagement(docker_dir)
    docker_manager.execute_init()

def handle_clone(args) -> None:
    """
    gitのクローン

    :param args:
        クローン操作に必要なパラメータまたは引数
    :type args: any
    :return: None
    """
    docker_dir = os.getcwd()
    print(f'カレントディレクトリ : {docker_dir}')

    git_manager = GitManagement(docker_dir)
    git_manager.execute()

def handle_stop(args) -> None:
    docker_dir = os.getcwd()
    print(f'カレントディレクトリ : {docker_dir}')

    docker_manager = DockerManagement(docker_dir)
    docker_manager.execute_stop()

def handle_build(args) -> None:
    docker_dir = os.getcwd()
    print(f'カレントディレクトリ : {docker_dir}')

    docker_manager = DockerManagement(docker_dir)
    docker_manager.execute_build()

def handle_run(args) -> None:
    docker_dir = os.getcwd()
    print(f'カレントディレクトリ : {docker_dir}')

    docker_manager = DockerManagement(docker_dir)
    docker_manager.execute()

def handle_reset_db(args) -> None:
    docker_dir = os.getcwd()
    print(f'カレントディレクトリ : {docker_dir}')

    docker_manager = DockerManagement(docker_dir)
    docker_manager.execute_reset_db()

def main():
    try:
        parser = argparse.ArgumentParser(
            description=(
                'プロジェクトの操作バッチ'
            ),
            formatter_class=argparse.RawTextHelpFormatter,
        )
        subparsers = parser.add_subparsers(dest='command', required=True)

        # 初期化
        run_parser = subparsers.add_parser(
            'init',
            help='初期化関連を行う',
            description=(
                'バックエンド・フロントエンドのプロジェクトリポジトリのクローン\n'
                'Dockerのプル・ビルド'
            ),
            formatter_class=argparse.RawTextHelpFormatter
        )
        run_parser.set_defaults(func=handle_init)

        # git のクローン
        run_parser = subparsers.add_parser(
            'clone',
            help='バックエンド・フロントエンドのプロジェクトリポジトリのクローン',
            description='バックエンド・フロントエンドのプロジェクトリポジトリのクローン'
        )
        run_parser.set_defaults(func=handle_clone)

        # ビルド
        run_parser = subparsers.add_parser(
            'build',
            help='imageのビルド',
            description='docker compose でビルド'
        )
        run_parser.set_defaults(func=handle_build)

        # コンテナの停止
        run_parser = subparsers.add_parser(
            'stop',
            help='コンテナの停止',
            description='docker compose で起動したコンテナの停止'
        )
        run_parser.set_defaults(func=handle_stop)

        # コンテナの起動
        run_parser = subparsers.add_parser(
            'run',
            help='コンテナの起動',
            description='docker compose で起動'
        )
        run_parser.set_defaults(func=handle_run)

        # DBの登録データのリセット
        run_parser = subparsers.add_parser(
            'reset',
            help='DBの登録データのリセット',
            description='docker compose で起動'
        )
        run_parser.set_defaults(func=handle_reset_db)

        args = parser.parse_args()
        args.func(args)

    except Exception as e:
        print(f'エラー : {e}')

if __name__ == '__main__':
    main()
