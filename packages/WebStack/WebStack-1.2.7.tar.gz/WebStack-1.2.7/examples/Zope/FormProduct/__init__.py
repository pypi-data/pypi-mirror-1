#!/usr/bin/env python

"A Zope product testing forms."

from Form import FormResource
from WebStack.Adapters.Zope import WebStackAdapterProduct
from Globals import InitializeClass

class FormProduct(WebStackAdapterProduct):
    meta_type = "Form product"
    def __init__(self, id):
        WebStackAdapterProduct.__init__(self, id, FormResource())

InitializeClass(FormProduct)

def addFormProduct(self):
    """
    The HTML form used to add the product.
    """

    return """
        <html>
            <head>
                <title>Add Form Product</title>
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

    product = FormProduct(id)
    self.Destination()._setObject(id, product)
    if REQUEST:
        return self.manage_main(self, REQUEST)

def initialize(context):
    context.registerClass(
        FormProduct,
        constructors = (addFormProduct, addProduct)
    )

# vim: tabstop=4 expandtab shiftwidth=4
