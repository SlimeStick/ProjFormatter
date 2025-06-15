from collections import deque
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TreeNodeWithDepth:
    node: Any
    depth: int


class LevelOrderTraverser:
    """
    Performs a level-order (breadth-first) traversal over a tree structure.
    Each node in the tree is expected to be iterable over its children.
    """

    def __init__(self, root, depth: Optional[int] = None):
        """
        :param root: The root node of the tree. Must be iterable to access children.
        :param depth: If specified, only nodes at this depth (0-based) will be returned.
                      Otherwise, all nodes will be returned.
        """
        self.queue = deque()
        self.queue.append(TreeNodeWithDepth(root, 0))
        self.depth = depth

    def __iter__(self):
        return self

    def __next__(self):
        while self.queue:
            current = self.queue.popleft()

            if self.depth is None or current.depth < self.depth:
                if len(current.node) > 0:
                    for child in current.node:
                        self.queue.append(TreeNodeWithDepth(child, current.depth + 1))

            if self.depth is None or self.depth == current.depth:
                return current.node

        raise StopIteration
