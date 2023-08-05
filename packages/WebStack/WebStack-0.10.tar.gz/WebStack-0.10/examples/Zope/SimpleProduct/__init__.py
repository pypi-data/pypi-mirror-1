#!/usr/bin/env python

"A simple Zope product."

from Simple import SimpleResource
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class SimpleProduct(WebStackAdapterProduct):
    meta_type = "Simple product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id, SimpleResource())

InitializeClass(SimpleProduct)

def addSimpleProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Simple Product</title>
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

    product = SimpleProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        SimpleProduct,
        constructors = (addSimpleProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
