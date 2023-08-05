"""
Shrubbery is a Smart Html Renderer (Using Blocks to Bind Expressions
RepeatedlY).

This is a simple templating engine designed to convert JSON data
into HTML or XML.

"""
import re

from BeautifulSoup import BeautifulSoup, NavigableString


# Basic regexp for matching all expressions in a template.
EXPR = re.compile(r"{([\w\.]+)}")


class Template(BeautifulSoup):
    def process(self, data, remove_empty_nodes=True):
        # Get all namespaces available in the template.
        nstree = _get_namespaces(self)
        return search(self.copy(), data, '', nstree, remove_empty_nodes) 

    def copy(self):
        return Template(unicode(self))
    

def search(tree, data, ns, nstree, remove_empty_nodes):
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

    # Now for every instance of ``data`` we will clone the
    # parent node, replacing the appropriate data values.
    if not isinstance(data, list): data = [data]
    data = [v for v in data if v != {}]  # remove empty {}s
    for i, values in enumerate(data):
        # Return node with the values applied.
        repl = apply(clone(node), ns, values)
        # Continue replacement in deeper namespaces.
        for k in nstree:
            repl = search(repl, values.get(k, {}), '%s%s.' % (ns, k), nstree.get(k, {}), remove_empty_nodes)
        parent.insert(index+i, repl)
    
    # Remove this node from parent.
    if data or remove_empty_nodes: node.extract()
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

    # Do the replacement.
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
