#!/usr/bin/env python

"A Zope product which tests Unicode output."

from Unicode import UnicodeResource
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class UnicodeProduct(WebStackAdapterProduct):
    meta_type = "Unicode product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id, UnicodeResource())

InitializeClass(UnicodeProduct)

def addUnicodeProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Unicode Product</title>
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

    product = UnicodeProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        UnicodeProduct,
        constructors = (addUnicodeProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
