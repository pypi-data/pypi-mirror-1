#!/usr/bin/env python

"A simple Zope product."

from Simple import SimpleResource
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class SimpleWithLoginProduct(WebStackAdapterProduct):
    meta_type = "Simple with login product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id,
            LoginRedirectResource(
                login_url="http://localhost:9080/tests/login",
                app_url="http://localhost:9080",
                resource=SimpleResource(),
                authenticator=LoginRedirectAuthenticator(secret_key="horses"),
                anonymous_parameter_name="anonymous",
                logout_parameter_name="logout"
            )
        )

InitializeClass(SimpleWithLoginProduct)

def addSimpleWithLoginProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Simple with Login Product</title>
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

    product = SimpleWithLoginProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        SimpleWithLoginProduct,
        constructors = (addSimpleWithLoginProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
