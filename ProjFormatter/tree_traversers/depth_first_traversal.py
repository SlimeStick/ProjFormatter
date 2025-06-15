class DepthFirstTraverser:
    """
    Performs a depth-first traversal over a tree structure.
    Each node in the tree is expected to be iterable over its children.
    """
    def __init__(self, root):
        """
        :param root: The root node of the tree. Must be iterable to access children.
        """
        self.root_iterator = root.iter()

    def __iter__(self):
        return self.root_iterator
