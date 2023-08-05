

class OutOfDateError(ValueError):
    """Manifest to be committed is not based on the currently committed version
    """

class NoChangesError(ValueError):
    """Manifest to be committed has no changes from the currently committed
    version"""

class ConflictError(ValueError):
    """Manifest to be committed has unresolved conflicts"""

class ParentConflictError(StandardError):
    """the item has more than one selected parent"""

class UpdateError(StandardError):
    """Update-related operation cannot proceed"""