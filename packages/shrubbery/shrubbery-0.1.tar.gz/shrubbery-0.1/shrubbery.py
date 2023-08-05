import re

from BeautifulSoup import BeautifulSoup, NavigableString


EXPR = re.compile(r"{([\w\.]+)}")


def Template(template, data):
    soup = BeautifulSoup(template)

    # Extract all namespaces from the template.
    nstree = _get_namespaces(soup)

    # Search for expressions in top namespace.
    return search(soup, data, '', nstree)


def search(tree, data, ns, nstree):
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
    data = [v for v in data if v]  # remove empty {}s
    for i, values in enumerate(data):
        # Return node with the values applied.
        repl = apply(clone(node), ns, values)
        for k in nstree:
            repl = search(repl, values.get(k, {}), '%s%s.' % (ns, k), nstree.get(k, {}))
        parent.insert(index+i, repl)
    
    return tree


def apply(tree, ns, data):
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


def _get_parent_namespaces(ns, namespaces):
    out = []
    if ns not in namespaces: out.append(ns)
    parent = ns
    index = 0
    while '.' in parent:
        index = ns.index('.', index)
        parent = ns[:index]
        index = index + 1
        if parent not in namespaces: out.append(parent)
    return out


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
    
        

if __name__ == '__main__':
    data = {"entry": [{'category': [{'term': 'weblog', 'label': 'Weblog'},
                                    {'term': 'python', 'label': 'Python stuff'}],
                       'content': {'content': '<p>This is my first post!</p>', 'type': 'html'},
                       'id': '1',
                       'title': 'First post',
                       'updated': '2007-01-23T18:18:43Z'},
                      {'content': {'content': '<p>This is the second post...</p>', 'type': 'html'},
                       'id': '0',
                       'title': ['One more post', 'With 2 titles'],
                       'updated': '2007-01-18T13:31:43Z'}],
            "title": "This is the title",
           }

    template = """<html>
<head> <title>{title}</title> </head>
<body> <h1>{title}</h1>

    <div id="{entry.id}"> <h2>{entry.title}</h2>
        <div class="{entry.content.type}">{entry.content.content} [this was: {entry.title}]</div>
        <p class="footnote">Updated on {entry.updated}</p>
        <ul><li class="{entry.category}"><a href="http://example.com/{entry.category.term}">{entry.category.label}</a></li></ul>
    </div>
</body>
</html>"""

    print Template(template, data)
