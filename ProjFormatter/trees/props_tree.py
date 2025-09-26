from ProjFormatter.trees.msbuild_tree import MSBuildTree


class PropsTree(MSBuildTree):
    def __init__(self, file_path: str):
        super().__init__(file_path)

    def format(self):
        pass
