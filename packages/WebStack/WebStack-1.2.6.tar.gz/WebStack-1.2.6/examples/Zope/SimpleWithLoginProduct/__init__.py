#!/usr/bin/env python

"A simple Zope product."

from Simple import SimpleResource
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Resources.ResourceMap import MapResource
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

# NOTE: Make sure this URL matches your Zope configuration.

server_url = "http://localhost:9080"

class SimpleWithLoginProduct(WebStackAdapterProduct):

    meta_type = "Simple with login product"

    def __init__(self, id, parent_url):
        WebStackAdapterProduct.__init__(self, id,
            MapResource({
                "simple" :
                    LoginRedirectResource(
                        login_url=parent_url + "/" + id + "/login",
                        app_url=server_url,
                        resource=SimpleResource(),
                        authenticator=LoginRedirectAuthenticator(secret_key="horses"),
                        anonymous_parameter_name="anonymous",
                        logout_parameter_name="logout"
                    ),
                "login" :
                    LoginResource(
                        LoginAuthenticator(
                            secret_key="horses",
                            credentials=(
                                ("badger", "abc"),
                                ("vole", "xyz"),
                            )
                        )
                    )
                })
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

    product = SimpleWithLoginProduct(id, self.DestinationURL())
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        SimpleWithLoginProduct,
        constructors = (addSimpleWithLoginProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
