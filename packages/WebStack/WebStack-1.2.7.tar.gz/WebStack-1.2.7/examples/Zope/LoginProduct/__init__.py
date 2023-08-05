#!/usr/bin/env python

"A Zope login product."

from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class LoginProduct(WebStackAdapterProduct):
    meta_type = "Login product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id,
            LoginResource(
                LoginAuthenticator(
                    secret_key="horses",
                    credentials=(
                        ("badger", "abc"),
                        ("vole", "xyz"),
                    )
                )
            )
        )

InitializeClass(LoginProduct)

def addLoginProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Login Product</title>
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

    product = LoginProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        LoginProduct,
        constructors = (addLoginProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
