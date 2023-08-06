## Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
"""
Any object implementing any interface defined here must be pickleable!
"""

from zope.interface import Interface, Attribute

# ISearchable, ITwiddler and IElement are good to know, even if you're
# just using Twiddler
class ISearchable(Interface):
    """
    ISearchable is a base interface for both ITwiddler and IElement
    which covers searching for elements to be manipulated.

    All methods in this interface only search within the subtree
    contained by the object on which the method is called. So, for an
    element, only the element and its children will be searched. For a
    twiddler, the whole tree of elements will be searched.
    """
    
    def getBy(**spec):
        """
        Find the first element which matches the spec.

        spec must contain exactly one key and one value. The key is
        the attribute to search by the and value is the value of that
        attribute to search for.

        If no element can be found that matches the spec, a KeyError
        will be raised.
        """

    def __getitem__(value):
        """
        Find the first element where value is present in one of the
        element's attributes that are indexed by the twiddler that
        contains this ISearchable.

        Indexes are searched in the order they were specified during
        instantiaton of the twiddler

        If no matching element can be found, a KeyError is raised.
        """
        
    twiddler = Attribute("""
        A reference to the object implementing ITwiddler that contains
        this object.

        NB: this is only intended for use by internal Twiddler methods
        """)
    
    node = Attribute("""
        A reference to the object implementing ISearchabeNode that
        this element wraps.

        NB: this is only intended for use by internal Twiddler methods
        """)

class ITwiddler(ISearchable):
    """
    This is the interface implemented by a twiddler object. It is
    the root of the tree of objects that make up a Twiddler.
    """

    def __init__(source,input=None,output=None,executor=None,
                 filters=(),indexes=()):
        """
        Creates a Twiddler from its constituent parts. This is
        predominantly a string or unicode forming the source and then,
        optionally an input parsers, and output renderer, a list of
        default filters and a list of attribute names to be indexed.

        Parameters as follows:

        source - the string or unicode that will be parsed to the
                 input parser to turn into a tree of nodes.

        input - a callable that will take the source as its input and
                return a tree of nodes where the tree implements ITree
                and each of the nodes implements INode. This must
                implement IInput.

        output - a callable that will take a tree of nodes, where the
                 tree implements ITree and each of the nodes
                 implements INode and returns whatever the desired
                 output is. In may cases this will be an encoded
                 string or unicode. This must implement IOutput.

        executor - a callable implementing IExecutor that will be used
                   to provide the the code to execute during rendering
                   of this ITwiddler. If an executor is provided,
                   anything it returns will override that returned by
                   the input parser.

        filters - a sequence of callables that each take a unicode and
                  return a unicode. These will be used, in the order
                  they are provided, to filter or transform text such
                  as attributes or tag values when the replace method
                  is called. Each of them must implement IFilter.
                  
        indexes - a sequence of strings or unicodes that specify the
                  names of the attributes to be indexed for searching in this
                  twiddler.

                  NB: There is a performance cost for each attribute
                      indexed, so the number indexed should be kept to
                      a minimum.

        NB: the callables provided in input, output and filters must
            be pickleable.
        """

    input = Attribute("""
        An object implementing IInput.

        If this attribute is set, then setSource should be called with
        the original or new source to re-parse it.

        NB: No checking is done when this attribute is set, be careful!
        """)

    output = Attribute("""
        An object implementing IOutput.

        NB: No checking is done when this attribute is set, be careful!
        """)

    executor = Attribute("""
        An object implementing IExecutor.

        If this attribute is set, then setSource should be called with
        the original or new source to re-call the executor and compile
        any source code that it returns.

        NB: No checking is done when this attribute is set, be careful!
        """)

    filters = Attribute("""
        An sequence of objects each implementing IFilter.

        NB: No checking is done when this attribute is set, be careful!
        """)

    indexes = Attribute("""
        A sequence of strings or unicodes that specify the
        names of the attributes to be indexed for searching in this
        twiddler.

        If this attribute is set, then setSource should be called with
        the original or new source for the new indexes to be populated.

        NB: No checking is done when this attribute is set, be careful!
        """)

    def setSource(source):
        """
        This parses the supplied source through the configured input
        using the configured indexes.

        If an executor is configured, this is then called to set up
        any code that should execute when the ITwiddler is rendered
        """

    def setFilters(*args):
        """
        This accepts a sequence of objects that implement IFilter and
        sets the default filters that will be applied to any parameter
        provided to the 'replace' method of an IElement.

        If any element in the sequence is True, the existing sequence
        of filters will be inserted into the new sequence in place of
        the True.
        """

    def clone():
        """
        Returns a copy of this twiddler that can be modified and
        manipulated completely independently.

        This method is called often so should be implemented to be as
        fast as possible.
        """

    def execute(*args,**kw):
        """
        Execute the function defined in the code block attached to
        this twiddler if one is present.

        args and kw will be passed to the function and must match its
        call signature or a TypeError will be raised.

        If no code block is defined, this method does nothing.

        Once a code block function has been executed, the whole code
        block is removed from the Twiddler.
        """

    def render(*args,**kw):
        """
        Render this Twiddler to the output generated by the output
        renderer after executing any code block attached to this
        twiddler.

        Code block execution is done by calling this twiddler's
        execute method with args and kw
        """
        
    node = Attribute("""
        A reference to the object implementing ITree that contains the
        node tree for this twiddler.

        NB: this is only intended for use by internal Twiddler methods
        """)

class IElement(ISearchable):
    """
    This represents a specific element associated with an object that
    implements ITwiddler.
    """

    def replace(content=True,tag=True,filters=True,attributes=None,**kwattributes):
        """
        Replace the specified parts of this element:

        content - the content of the element, can be replaces with another
                TwiddlerElement
        
        tag - the tag name of the element

        filters - a sequence of filters which overrides the default filters.
                  True can be put in any place in the sequence and the default
                  filters will be inserted into the filter chain at that point.

        attributes - an optional dictionary that can't be passed as keyword
                     arguments for whatever reason, such as the 'class' attribute.

        Further keyword arguments replace or add attributes of the same name as
        the argument.

        There are two special values that can be passed of the value of content,
        tag or any attribute:

        True - leave the attribute, tag or tag value as it currently is

        False - remove the attribute or tag value completely. In the case of
                the tag parameter, passing False will remove the tag itself but
                still leave the content of the tag intact.
        """

    def repeater():
        """
        Removes this element and all its children and returns an object
        implementing IRepeater for this element.
        """
        
    def clone():
        """
        Returns a copy of this element.

        This copy is not inserted into the source Twiddler and can safely be
        inserted into any location in any Twiddler with a normal replace
        operation.
        """

    def remove():
        """
        Remove this element and all its children.
        """

    node = Attribute("""
        A reference to the object implementing INode that this element wraps.

        NB: this is only intended for use by internal Twiddler methods
        """)

class IRepeater(Interface):
    """
    This represents a repeater for a specific element associated with an object
    that implements ITwiddler.
    """

    def repeat(*args,**kw):
        """
        This method is used to repeat specific Twiddler elements.

        Each time it is called, a new copy of the element it was created with
        is inserted at the place where the repeater's element came from in the
        Twiddler but after any elements that have already been inserted by this
        repeater.

        The arguments and keyword parameters are use to preform a
        'replace' operation on the newly inserted element once it has been
        inserted into the Twiddler.
        """

# These interfaces are only useful to know if you're writing new inputs or outputs
class IInput(Interface):
    """
    This is the interface implemented by input parsers suitable for
    use with a twiddler.

    NB: The object doesn't have to be marked as implementing this
        interface.
    """

    def __call__(source,indexes):
        """
        Parse the source into a tree of nodes and, optionally, a block
        of python source or a callable object.

        parameters are as follows:
        
        source - the source text to be parsed. This is usually either
                 a string or unicode.

        indexes - a sequence of strings or unicodes specifying the
                  names of the attributes that should be indexed in
                  the ITree returned by this method.

        This method is free to raise errors if the type of the source
        parameter is not appropriate or if the contents of the source
        cannot sensibly be parsed into a tree of nodes.

        The method must return a tuple of the form:
        (tree,executor)

        tree - an object implementing ITree. Any subnodes of that
               object must implement INode.

        executor - a callable implementing IExecutor that will be
                   called whenever the execute or render methods of
                   the resulting Twiddler are called.

        If False is returned as the executor, then any existing
        executor on the ITwiddler will be removed.

        if None is returned as the executor, then any existing
        executor on the ITwiddler will be left in place.
        """
        
class IOutput(Interface):
    """
    This is the interface implemented by output renderers suitable for
    use with a twiddler.

    NB: The object doesn't have to be marked as implementing this
        interface.
    """

    def __call__(root,*args,**kw):
        """
        This should process the tree of nodes provided into suitable
        output which is returned from this method. Output is usually
        an encoded string or unicode, but there is no hard requirement
        for this.

        'root' will be an object implementing ITree and all of its
        subnodes will implement INode.

        The object providing IOutput will called as part from a call
        to the render method. 'args' and 'kw' contain the parameters
        passed to the render method. As such, all objects providing
        IOutput must be capable of accepting any parameters to their
        call method.
        """

class IExecutor(Interface):
    """
    This is the interface implemented by executors suitable for
    providing code to be executed during the rendering of an ITwiddler.
    NB: The object doesn't have to be marked as implementing this
        interface.
    """

    def __call__():
        """
        When called, this should return a tuple of the form:

        (source,code)

        The elements of the tuple should contain the following:
    
        source - a string containing python source code that defines,
                 at most, one function. That function will be executed
                 whenever the execute or render methods of the
                 resulting Twiddler are called.

        callable - a callable object that will be called whenever the
                   execute or render methods of the resulting Twiddler
                   are called. This callable must be pickleable.

        Only one of source or callable should be used. The one not
        being used should be returned as None. If both source and
        callable are None then no code will be intrinsically executed
        when the execute or render methods of the resulting Twiddler
        are called.
        """


class IFilter(Interface):
    """
    This is the interface implemented by filters suitable for use with
    a twiddler. 
    
    NB: The object doesn't have to be marked as implementing this
        interface.
    """

    def __call__(value):
        """
        This should perform the necessary filtering or
        transformation.

        value will be a unicode and a unicode should be returned.
        """
    
class ISearchableNode(Interface):
    """
    Both ITree and INode implement this common set of functionality.
    The searching defined here should always only search the object
    implementing this interface and any of its children.
    """
    
    def findByAttribute(name,value):
        """
        Find the first node where the value can be found in the
        attribute identified by the name parameter.

        If no suitable node can be found, a KeyError will be raised.
        """

    def search(value):
        """
        Find the first node where value is present in one of the
        node's attributes that are indexed by the ITree that
        contains this ISearchableNode.

        Indexes are searched in the order they were specified in the
        parameter passed to the input parser that created this INode
        and its associated ITree

        If no matching node can be found, a KeyError is raised.
        """

class ITree(ISearchableNode):
    """
    This is a tree of nodes and serves as the root of the internal
    implementation that must be returned by an input parser. It must
    support indexing such that the searching methods provided by
    ISearchableNode for the tree and any of its subnodes can execute
    quickly.
    """

    def getroot():
        """
        Returns the root of the tree as an object implementing INode.
        """
        
class INode(ISearchableNode):
    """
    All nodes returned in a tree returned by an input parser must
    implement this interface and should be marked with it in order for
    tests to pass.
    """

    tag = Attribute("""
        This is the identifier for the tag represented by this node.
        It must either be a unicode, None or an object.
        
        If it is a unicode, then it is assumed this INode represents a
        normal tag and the unicode represents the identifier for the
        tag.
        
        If it is None, this is an indication to the output renderer
        that this tag and its attributes should not be rendered. The
        contents of the tag should be rendered regardless of the value
        of this attribute.

        If it is an object, then this signals to the output renderer
        that this isn't really a tag but something that needs special
        handling. Common examples are html or xml comments, xml
        declarations and doctypes.

        If you're implementing your own input parser, you're free to
        return new types of object but bear in mind that these won't
        render correctly unless the output renderer knows what to do
        with them.

        The default output renderer is a good place to look for
        examples of the common types of object to expect.
        """)

    text = Attribute("""
        This is the textual content of the tag represented by this node.
        It must either be a unicode or None.
        
        If it is None, this is an indication to the output renderer
        that this tag has no content.
        """)

    tail = Attribute("""
        This is the text that follows the tag represented by this node
        up until the start of the next tag. It must either be a
        unicode or None.
        
        If it is None, this is an indication to the output renderer
        that no text should be rendered between the end of this tag
        and the start of the following tag.
        """)
    
    parent = Attribute("""
        This is a reference to the node that contains this node.
        It may be None to indicate that this node is not part of a
        tree.
        """)

    def index(node):
        """
        Returns the index of node in the children of this node.
        Raises a ValueError if node is not a child of this node.
        """

    def __getitem__(index):
        """
        Returns the child node at the specified index.
        If the index does not point to a node, then an IndexError will
        be raised. 
        """

    def items():
        """
        This returns a sequence of tuples containing the data for the
        attributes of the tag represented by this node.

        Each tuple is of the form (attribute_name,attribute_value).
        """

    def insert(index,node):
        """
        This inserts the supplied node at the specified index into the
        children of this node.

        Exceptions may be raised if the index is invalid and really
        bad things may happen if node does not implement INode.

        This insertion should update any indexing needed by the tree
        containing this node to efficiently implement ISearchableNode.
        """

    def getchildren():
        """
        This returns a sequence of all child nodes in rendering order.
        """

    def remove(node):
        """
        This removes the supplied node from the list of children of
        this node.

        Exceptions will be raised if node is not a child of this
        node.
        """

    def delete(attribute):
        """
        This deletes the specified attribute of the tag this node
        represents.
        """

    def set(attribute,value):
        """
        This sets the specified attributed to the supplied value.
        If the attribute does not exist, it is created.
        """
