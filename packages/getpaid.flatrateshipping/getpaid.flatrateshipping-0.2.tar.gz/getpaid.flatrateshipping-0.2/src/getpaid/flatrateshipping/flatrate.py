# Copyright (c) 2007 ifPeople, Kapil Thangavelu, and Contributors
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
$Id: null.py 1143 2007-12-31 02:16:19Z kapilt $
"""

from zope import interface
from getpaid.core import interfaces, options
from interfaces import IFlatRateShippingSettings
from getpaid.core.interfaces import IShippableLineItem

FlatRateShippingSettings = options.PersistentOptions.wire(
    "FlatRateShippingSettings",
    "getpaid.flatrateshipping",
    IFlatRateShippingSettings
    )

class FlatRateShippingAdapter( object ):

    interface.implements( interfaces.IShippingMethod )
    options_interface = IFlatRateShippingSettings

    def __init__( self, context ):
        self.context = context
        self.settings = IFlatRateShippingSettings( self.context )
        
    def getCost( self, order ):
        settings = self.settings
        if(settings.flatrate_option == "Percentage"):
            return self.settings.flat_rate
        else: # we're calculating the percentage
            items = filter( IShippableLineItem.providedBy, order.shopping_cart.values() )
            cost = 0
            for item in items:
                cost += item.cost
            shipcost = cost * (settings.flatrate_percentage / 100)
            if shipcost > settings.flatrate_max:
                shipcost = settings.flatrate_max
            return shipcost
