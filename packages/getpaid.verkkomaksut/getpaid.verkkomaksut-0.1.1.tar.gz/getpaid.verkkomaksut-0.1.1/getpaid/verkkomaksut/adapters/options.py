"""
"""
from getpaid.core.options import PersistentOptions
from getpaid.verkkomaksut.interfaces import IVerkkomaksutOptions

VerkkomaksutOptions = PersistentOptions.wire("Verkkomaksut",
                                             "getpaid.verkkomaksut",
                                             IVerkkomaksutOptions )
