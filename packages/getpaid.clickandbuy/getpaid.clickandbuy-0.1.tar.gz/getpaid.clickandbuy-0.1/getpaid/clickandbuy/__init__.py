"""
"""

from getpaid.core.options import PersistentOptions
import interfaces

ClickAndBuyStandardOptions = PersistentOptions.wire("ClickAndBuyStandardOptions",
                                               "getpaid.ClickAndBuy",
                                               interfaces.IClickAndBuyStandardOptions )
