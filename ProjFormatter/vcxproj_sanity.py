
class SanityChecker:
    def __init__(self,
                 check_wildcards: bool = True,
                 check_lists : bool = True,
                 check_order : bool = True,
                 check_macros : bool = True,
                 check_targets : bool = True):
        """
        Receives elements one after the other and makes sure that they don't break the vcxproj format.
        This is done due to Microsoft's documentation that manual editing mistakes can cause the IDE to crash
        or behave in unexpected ways.

        :param check_wildcards: Whether to check for wildcard usage in elements.
        :param check_lists: Whether to check for list usage in elements.
        :param check_order: Whether to validate elements order.
        :param check_macros: Whether to check for macro usage in project item paths.
        :param check_targets: Whether to check that all targets are imported at the end of the file.
        """
        # There are 2 types of rules we check
        # 1. Rules that apply to all elements no matter where they are
        # 2. Order rules

        self.check_wildcards = check_wildcards
        self.check_lists = check_lists
        self.check_order = check_order

        self._expected_order = None
        self.check_macros = check_macros
        self.check_targets = check_targets

    def check_elements(self, elements):

