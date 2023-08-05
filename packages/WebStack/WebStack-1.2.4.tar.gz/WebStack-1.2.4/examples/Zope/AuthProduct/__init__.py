#!/usr/bin/env python

"A Zope product which tests authentication."

from Auth import AuthResource, AuthAuthenticator
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class AuthProduct(WebStackAdapterProduct):
    meta_type = "Auth product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id, AuthResource(), AuthAuthenticator())

InitializeClass(AuthProduct)

def addAuthProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Auth Product</title>
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

    product = AuthProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        AuthProduct,
        constructors = (addAuthProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
