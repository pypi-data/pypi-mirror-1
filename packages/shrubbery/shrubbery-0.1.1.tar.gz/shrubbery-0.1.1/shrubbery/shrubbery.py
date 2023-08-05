"""
Shrubbery is a Simple Html Renderer (Using Blocks to Bind Expressions
RecursivelY).

This is a simple templating engine designed to convert JSON data
into HTML or XML. Of course since typical Python objects (lists,
dicts, strings, numbers) are also JSON objects, the same can be
said of any other Python template -- but shrubbery has a few notable
differences.

First, shrubbery templates resemble `templess
<http://johnnydebris.net/xmlns/templess>`_ in that they contain *no
logic*: there are no loops, no variable formatting, no embedded
Python code. Instead, the logic is dictated by the data: multiple
values will result in nodes being copied to fit the data.

Here's a practical example: you want to write a weblog with several
entries. Here's one possible way to write a shrubbery template for
this kind of application::

    >>> template = '''<html>
    ... <head> <title>{title}</title> </head> 
    ... <body> <h1>{title}</h1>
    ...     <div id="{entry.id}"> <h2>{entry.title}</h2>
    ...         <div class="{entry.content.type}">{entry.content.content}</div>
    ...         <p class="footnote">Updated on {entry.updated}</p>
    ...         <ul>
    ...             <li class="{entry.category}">
    ...                 <a href="http://example.com/{entry.category.term}">{entry.category.label}</a>
    ...             </li>
    ...         </ul>
    ...     </div>
    ... </body>
    ... </html>'''

When now should pass a JSON/Python object to the template. Suppose
we have two entries with the following content::

    >>> data = {"entry": [{'category': [{'term': 'weblog', 'label': 'Weblog'},
    ...                                 {'term': 'python', 'label': 'Python stuff'}],
    ...                    'content': {'content': '<p>This is my first post!</p>', 'type': 'html'},
    ...                    'id': '0',
    ...                    'title': 'First post',
    ...                    'updated': '2007-01-17T18:18:43Z'},
    ...                   {'content': {'content': '<p>This is the second post...</p>', 'type': 'html'},
    ...                    'id': '1',
    ...                    'title': 'One more post',
    ...                    'updated': '2007-01-18T13:31:43Z'}],
    ...         "title": "This is the title",
    ...        }

When this data is applied to the template, the top <div> will be
replicated twice, once for each entry. The same will happen with
the ``category`` expression for the first entry. The final result
is this (indented for clarity)::
    
    <html>
        <head> <title>This is the title</title> </head>
        <body> <h1>This is the title</h1>
            <div id="0"> <h2>First post</h2>
                <div class="html"><p>This is my first post!</p></div>
                <p class="footnote">Updated on 2007-01-17T18:18:43Z</p>
                <ul>
                    <li>
                        <a href="http://example.com/weblog">Weblog</a>
                    </li>
                    <li>
                        <a href="http://example.com/python">Python stuff</a>
                    </li>
                </ul>
            </div>
            <div id="1"> <h2>One more post</h2>
                <div class="html"><p>This is the second post...</p></div>
                <p class="footnote">Updated on 2007-01-18T13:31:43Z</p>
                <ul></ul>
            </div>
        </body>
    </html>

"""
import re

from BeautifulSoup import BeautifulSoup, NavigableString


# Basic regexp for matching all expressions in a template.
EXPR = re.compile(r"{([\w\.]+)}")


def Template(template, data):
    """
    Apply data to template and returns a BeautifulSoup tree object.
    
    """
    soup = BeautifulSoup(template)

    # Extract all namespaces from the template.
    nstree = _get_namespaces(soup)

    # Search for expressions in top namespace.
    return search(soup, data, '', nstree)


def search(tree, data, ns, nstree):
    """
    Search for all expressions inside a given namespace.

    This function finds all expressions inside a given namespace
    (say, ``entry``). After that it locates the uppermost node
    common to all nodes, and replicates it according to the number
    of elements in the applied data. Each node is then processed
    to replace the expressions with the proper values.

    """
    # Search for all expressions inside a given namespace.
    regexp = re.compile(r"{%s[\w\.]*}" % ns.rstrip('.'))
    nodes = tree.findAll(replaceable(regexp)) + tree.findAll(text=regexp)
    if not nodes: return tree

    # Get the node in common and its parent.
    node = find_common_node(nodes)
    parent = node.parent
    index = parent.contents.index(node)
    # Remove this node from parent.
    node.extract()

    # Now for every instance of ``data`` we will clone the
    # parent node, replacing the appropriate data values.
    if not isinstance(data, list): data = [data]
    data = [v for v in data if v != {}]  # remove empty {}s
    for i, values in enumerate(data):
        # Return node with the values applied.
        repl = apply(clone(node), ns, values)
        for k in nstree:
            repl = search(repl, values.get(k, {}), '%s%s.' % (ns, k), nstree.get(k, {}))
        parent.insert(index+i, repl)
    
    return tree


def apply(tree, ns, data):
    """
    Apply replacement in expressions.

    This function replaces the expressions with the values in ``data``.

    """
    # Find all replaceable nodes from this namespace.
    regexp = re.compile(r"{%s}" % ns.rstrip('.'))
    nodes = tree.findAll(replaceable(regexp)) + tree.findAll(text=regexp)

    # Normalize data. Data can be a dict when it's used
    # as a stub for defining the topmost element to
    # repeat.
    if isinstance(data, dict): data = ''
    data = unicode(data)

    for node in nodes:
        if isinstance(node, NavigableString):
            repl = regexp.sub(data, node.string)
            if node.parent: node.replaceWith(repl)
        else:
            if node.string:
                repl = regexp.sub(data, node.string)
                node.next.replaceWith(repl)
            for k, v in node.attrs:
                node[k] = regexp.sub(data, v).strip()
                if not node[k]: del node[k]

    return tree


def find_common_node(nodes):
    """
    Return the lowest node in common given a list of nodes.

    """
    # Senseless for a single node.
    if len(nodes) == 1: return nodes[0]

    # Get a list of all parents.
    parents = [[node] + node.findParents() for node in nodes]
    # Here we use the smallest list, iterating over each element
    # and checking if the candidate appears in all list of 
    # parents.
    parents.sort(key=len)
    for candidate in parents.pop(0):
        for other_parents in parents:
            if candidate not in other_parents: break
        else:
            return candidate


def _get_namespaces(soup):
    """
    Get all namespaces from the template.

    """
    namespaces = {}
    nodes = soup.findAll(replaceable())
    for node in nodes:
        for ns in EXPR.findall(node.string or ''):
            ns = ns.split('.')
            root = namespaces
            for item in ns:
                root = root.setdefault(item, {})
        for k, v in node.attrs:
            for ns in EXPR.findall(v):
                ns = ns.split('.')
                root = namespaces
                for item in ns:
                    root = root.setdefault(item, {})

    return namespaces


def clone(node):
    """
    Clone a node.

    We simply parse the HTML from the node to be copied. Yes, I'm lazy.

    """
    return BeautifulSoup(unicode(node))


def replaceable(regexp=EXPR):
    """
    Return function to find nodes that are replaceable in a given namespace.
    
    """
    def func(tag):
        if tag.string and regexp.search(tag.string): return True
        for (k, v) in tag.attrs:
            if regexp.search(v): return True
        return False
    return func


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
