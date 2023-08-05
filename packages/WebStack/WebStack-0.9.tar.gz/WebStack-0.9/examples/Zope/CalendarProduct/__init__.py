#!/usr/bin/env python

"A Zope calendar product."

from Calendar import DirectoryResource
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class CalendarProduct(WebStackAdapterProduct):
    meta_type = "Calendar product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id, DirectoryResource())

InitializeClass(CalendarProduct)

def addCalendarProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Calendar Product</title>
            </head>
            <body>
                <form action="addProduct">
                    id <input name="id" type="text"><br>
                    <input name="add" type="submit" value="Add!">
                </form>
            </body>
        </html>
        """

def addProduct(self, id, REQUEST=None):
    """
    The function used to add the product.
    """

    product = CalendarProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        CalendarProduct,
        constructors = (addCalendarProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
