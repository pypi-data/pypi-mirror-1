<?python

chdocs = 'http://www.cleverharold.org/documentation'

?>
<html xmlns:py="http://purl.org/kid/ns#">
<div py:def="main()">

<h1>Documentation</h1>
<p>
This page is a jumping off point to the official Clever Harold documentation.
</p>


<h3><a name="introduction">Introduction</a></h3>
<p>
Clever Harold has a growing collection of documentation.  (Yes, that's
a nice way of saying it's not really big yet).  There should be plenty
to get you started, but please don't hesitate to ask questions on the
mailing list if you can't find something.
</p>


<h3><a name="programs">Writing Programs, aka Controllers</a></h3>
<p>
Clever Harold makes quick work of writing web programs (called
Controllers in an MVC architecture).
</p>
<p>
To get started, add a Python module to your project <code>controllers</code>
module, and fill it with your classes and functions.  Mark the
appropriate ones with <code>exposed=True</code>, and then call them via your
browser.  It really is that easy -- no imports, no dances.  (Harold
doesn't dance).
</p>

<p>See the Official <a href="${chdocs}/programs"> Program Authoring
Guide</a> on the Clever Harold web site.
</p>


<h3><a name="templates">Writing Templates, aka Views</a></h3>
<p>
In a Clever Harold application, the framework does the work of including
your site-wide templates.  You don't have to do anything more than specify
the layout template in your project config file.  No mindless inclusion of 
included modules, no repetitious repeating over and over and over the same
layout markup.
</p>

<p>Clever Harold applications publish templates, like Kid Templates,
and Cheetah Templates, and can publish markup, such as static HTML,
Restructured Text, and Markdown files.  See the
Official <a href="${chdocs}/templates"> Template Authoring Guide</a>
on the Clever Harold web site for more information.
</p>


<h3><a name="caching">Caching</a></h3>
<p>
Clever Harold has modules for caching function and page results to
memory, <code>memcached</code>, and/or to disk.  Refer to
the <a href="${chdocs}/caching">Caching Support</a> for the latest
documentation.
</p>

<h3><a name="sessions">Sessions</a></h3>
<p>
Clever Harold uses the session modules provided by your web server.
Currently, that includes Apache/mod_python, Flup, and Paste. Refer to
the <a href="${chdocs}/sessions">Sessions Support</a> for more information.
</p>


<h3><a name="forms">Forms</a></h3>
<p>
Clever Harold handles your HTML forms on the server like you want
them -- they redirect errors back to the form template itself, or they
can be set up to respond via asynchronous (AJAX) calls.  See
the <a href="${chdocs}/forms">Forms Tutorial</a> for more
information.
</p>



</div>

<div id="sidebar" py:def="sidebar()">
    <div class="featurebox" style="padding:10px;">
	<h3>Quick Links</h3>
	<ul style="padding-left:0">
	    <li><a href="${chdocs}/programs">Program Authoring Guide</a></li>
	    <li><a href="${chdocs}/templates">Template Authoring Guide</a></li>
	    <li><a href="${chdocs}/caching">Caching Support</a></li>
	    <li><a href="${chdocs}/caching">Sessions Support</a></li>
	    <li><a href="${chdocs}/forms">Forms Tutorial</a></li>
	</ul>
    </div>
</div>
</html>
