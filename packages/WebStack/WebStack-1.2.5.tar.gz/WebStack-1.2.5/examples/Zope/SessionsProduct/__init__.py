#!/usr/bin/env python

"A Zope product testing sessions."

from Sessions import SessionsResource
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class SessionsProduct(WebStackAdapterProduct):
    meta_type = "Sessions product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id, SessionsResource())

InitializeClass(SessionsProduct)

def addSessionsProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Sessions Product</title>
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

    product = SessionsProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        SessionsProduct,
        constructors = (addSessionsProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
