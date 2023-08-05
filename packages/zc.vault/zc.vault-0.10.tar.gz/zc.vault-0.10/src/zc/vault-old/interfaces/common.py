import zope.interface.common.mapping


class IBidirectionalMapping(zope.interface.common.mapping.IMapping):
    """values and keys are unique; value type homogenous; key type homogenous.
    """

    def getKey(value, default=None):
        """return key for value, or None"""


class IOrderedMapping(zope.interface.common.mapping.IMapping):
    """items, values, keys, and __iter__ returns in the specified order.
    Adding items extends the order."""

    def updateOrder(order):
        """Revise the order of keys, replacing the current ordering.

        order is an iterable containing the set of existing keys in the new
        order. `order` must contain ``len(keys())`` items and cannot contain
        duplicate keys.

        Raises ``TypeError`` if order is not iterable or any key is not
        hashable.

        Raises ``ValueError`` if order contains an invalid set of keys.
        """


class IBidirectionalNameMapping(IBidirectionalMapping, IOrderedMapping):
    """all keys are unicode, all values are adaptable to IKeyReference."""
