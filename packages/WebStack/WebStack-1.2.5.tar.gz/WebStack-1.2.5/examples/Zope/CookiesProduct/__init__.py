#!/usr/bin/env python

"A Zope product which tests cookie handling."

from Cookies import CookiesResource
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class CookiesProduct(WebStackAdapterProduct):
    meta_type = "Cookies product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id, CookiesResource())

InitializeClass(CookiesProduct)

def addCookiesProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Cookies Product</title>
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

    product = CookiesProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        CookiesProduct,
        constructors = (addCookiesProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
