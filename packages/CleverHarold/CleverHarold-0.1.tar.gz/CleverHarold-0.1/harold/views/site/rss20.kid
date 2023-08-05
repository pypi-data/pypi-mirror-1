<?xml version="1.0"?>
<?python

import cElementTree

channel_options = """language copyright managingEditor webMaster
pubDate lastBuildDate category generator docs ttl rating
""".split()


def simple_tag(tag, text):
    ele = cElementTree.Element(tag)
    ele.text = text
    return ele


def object_tag(obj, tag, default=None, required=False):
    try:
        text = obj[tag]
    except (KeyError, AttributeError, TypeError, ):
        text = getattr(obj, tag, default)
    if text is None and required:
        raise ValueError("Required value '%s' missing." % tag)
    if text is None:
        return None
    ele = cElementTree.Element(tag)
    ele.text = text
    return ele


def include_image(img):
    return (
        object_tag(img, 'url', required=True),
        object_tag(img, 'title', required=True),
        object_tag(img, 'link', required=True),
        object_tag(img, 'width', 88),
        object_tag(img, 'height', 31),
        object_tag(img, 'description'),
    )


def include_textinput(inp):
    return (
        object_tag(inp, 'title', required=True),
        object_tag(inp, 'description', required=True),
        object_tag(inp, 'name', required=True),
        object_tag(inp, 'link', required=True),
    )


def include_item(item):
    title = object_tag(item, 'title')
    description = object_tag(item, 'description')
    if title is None and description is None:
        raise ValueError('RSS channel item must have either title or description.')
    return (
        title,
        object_tag(item, 'link'),
        description,
        object_tag(item, 'author'),
        object_tag(item, 'category'), ## needs optional domain attribute
        object_tag(item, 'comments'), 
        object_tag(item, 'enclosure'), ## needs required enclosure, length and type attributes
        object_tag(item, 'guid'), ## needs optional isPermaLink attribute
        object_tag(item, 'pubDate'),
        object_tag(item, 'source'), ## needs required url attribute
    )

?>
<rss version="2.0" xmlns:py="http://purl.org/kid/ns#">
    <channel>
	<!--! required channel elements -->
	<title py:content="title" />
	<link py:content="link" />
	<description py:content="description" />

	<!--! optional channel elements -->  
	<block py:for="option in channel_options" 
                   py:if="defined(option)"
	               py:content="simple_tag(option, value_of(option))" 
                           py:strip="" />
	<cloud py:if="defined('cloud')" py:attrs="cloud" />
	<skipHours py:if="defined('skipHours')">
	    <hour py:for="hour in skipHours" py:content="hour" />
	</skipHours>
	<skipDays py:if="defined('skipDays')">
	    <day py:for="day in skipDays" py:content="day" />
	</skipDays>
	<image py:if="defined('image')" py:content="include_image(image)" />
	<textInput py:if="defined('textInput')" 
                   py:content="include_textinput(textInput)" />

	<!--! items -->
	<item py:for="item in items" py:content="include_item(item)" />

   </channel>
</rss>
