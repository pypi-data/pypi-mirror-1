"""
"""

from getpaid.core.options import PersistentOptions
import interfaces

PagseguroStandardOptions = PersistentOptions.wire("PagseguroStandardOptions",
                                               "getpaid.pagseguro",
                                               interfaces.IPagseguroStandardOptions )

