## Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from zope.interface import Interface, Attribute

class IConfigurableComponent(Interface):

    def configureForm():
        """
        This should return a lump of html containing form definitions
        and the like to be inserted into a <form> tag on the Configure
        tab.

        The <form> tag and 'Save Changes' button will already be
        generated.
        """

    def configure(form):
        """
        This should use information from the supplied form to
        configure this object.

        'form' is a dictionary equivalent to REQUEST.form
        """

class IInputFactory(Interface):

    def __call__():
        """
        Returns an object implementing twiddler.interfaces.IInput
        """

class IExecutorFactory(Interface):

    def __call__():
        """
        Returns an object implementing twiddler.interfaces.IExecutor
        """

class IOutputFactory(Interface):

    def __call__():
        """
        Returns an object implementing twiddler.interfaces.IOutput
        """

class IFilterFactory(Interface):

    def __call__():
        """
        Returns an object implementing twiddler.interfaces.IFilter
        """

