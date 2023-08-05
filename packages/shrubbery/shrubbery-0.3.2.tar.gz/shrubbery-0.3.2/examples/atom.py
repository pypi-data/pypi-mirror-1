from shrubbery.template import Template

template = Template("""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

    <title type="html">Comments for post {post_id} from {owner}</title>
    <link rel="self" href="{root}/atom?owner={owner}&post_id={post_id}"/>
    <updated>{updated}</updated>
    <author>
        <name>{owner}</name>
        <uri>{owner}</uri>
    </author>
    <id>{owner}#parlatorio_{post_id}</id>

    <entry>
        <link href="{root}/comments?owner={owner}&post_id={post_id}#{comment.id}"/>
        <title>Comment by {comment.name}</title>
        <id>{root}/comments?owner={owner}&amp;post_id={post_id}#{comment.id}</id>
        <updated>{comment.updated}</updated>
        <content type="html">{comment.content}</content>
    </entry>
</feed>""")

data = {"entry": [{'category': [{'term': 'weblog', 'label': 'Weblog'},
                                {'term': 'python', 'label': 'Python stuff'}],
                   'content': {'content': '<p>This is my first post!</p>', 'type': 'html'},
                   'id': '1', 
                   'title': 'First post',
                   'updated': '2007-01-23T18:18:43Z'},
                  {'content': {'content': '<p>This is the second post...</p>', 'type': 'html'},
                   'id': '0', 
                   'title': 'One more post',
                   'updated': '2007-01-18T13:31:43Z'}],
        "title": "This is the title"}

print template.process(data, escape=True).prettify()
