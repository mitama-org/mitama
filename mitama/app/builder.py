import inspect
import os


class Builder(object):
    """Appにメタ情報を入力して生成するビルダー

    プロジェクトディレクトリのパスやインストール先、プロジェクト内のアプリ用ディレクトリのパスをAppに設定し、インスタンスを返却します。
    特にこれを弄るケースは想定していませんが、独自の挙動を付けたかったら継承して作っても良いかもしれません。
    アプリのパッケージ直下のAppBuilderが起動されるので、:file:`__init__.py` に :samp:`class AppBuilder(Builder)` を定義してください。
    """

    app = None

    def __init__(self):
        self.data = {}
        pass

    def set_path(self, path):
        self.data["path"] = path

    def set_screen_name(self, screen_name):
        self.data["screen_name"] = screen_name

    def set_package(self, package):
        self.data["package"] = package

    def set_project_dir(self, path):
        self.data["project_dir"] = path

    @property
    def path(self):
        return self.data.get("path")

    @property
    def screen_name(self):
        return self.data.get("screen_name")

    @property
    def package(self):
        return self.data.get("package")

    @property
    def project_dir(self):
        return self.data.get("project_dir")

    @property
    def project_root_dir(self):
        return self.data.get("project_root_dir")

    def build(self):
        install_dir = os.path.dirname(inspect.getfile(self.__class__))
        self.data["install_dir"] = install_dir
        return self.app(**self.data)

