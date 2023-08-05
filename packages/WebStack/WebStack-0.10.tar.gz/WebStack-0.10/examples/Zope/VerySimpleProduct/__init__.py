#!/usr/bin/env python

"A very simple Zope product."

from VerySimple import VerySimpleResource
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class VerySimpleProduct(WebStackAdapterProduct):
    meta_type = "VerySimple product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id, VerySimpleResource())

InitializeClass(VerySimpleProduct)

def addVerySimpleProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add VerySimple Product</title>
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

    product = VerySimpleProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        VerySimpleProduct,
        constructors = (addVerySimpleProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
