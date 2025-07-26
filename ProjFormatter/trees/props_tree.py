from ProjFormatter.trees.xml_tree import XMLTree


class PropsTree(XMLTree):
    def __init__(self, file_path: str):
        super().__init__(file_path)
