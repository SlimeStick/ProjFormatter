from ProjFormatter.utils.element_utils import (get_children, get_child_count, merge_children, are_elements_of_same_type,
                                               are_relevant_elements)


def merge_elements_of_same_type(root):
    for child in get_children(root):
        merge_elements_of_same_type(child)

    index = 0
    skip_index = 0

    while True:
        if index + 1 >= get_child_count(root):
            break
        if index + 1 + skip_index >= get_child_count(root):
            index += 1
            skip_index = 0

        child1 = root[index]
        child2 = root[index + 1 + skip_index]
        if are_elements_of_same_type(child1, child2):
            merge_children(root, child2, child1)
            # Don't increment index as one child2 was deleted
        else:
            if not are_relevant_elements(child1, child2):
                skip_index += 1
            else:
                index += 1
                skip_index = 0
