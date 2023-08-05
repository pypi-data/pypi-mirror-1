<?python

lipsum = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit. 
Proin dictum, dolor ac sollicitudin gravida, mauris sapien fringilla leo, at blandit enim ipsum et magna.
Curabitur et elit eget diam ultricies egestas. 
Lorem ipsum dolor sit amet, consectetuer adipiscing elit. 
Phasellus eget nisi. 
Cras euismod nunc eu risus. Pellentesque vitae ligula.
Phasellus eget sem vel nibh porta iaculis.
Nulla sed neque.
"""

lipsum_sentances = lipsum.split('\n')
fruits = ['Apple', 'Pear', 'Cherry', 'Plum', ]

?>
<html xmlns:py="http://purl.org/kid/ns#">
<title py:def="title()">Page Title - New Application</title>


<block py:def="default_stylesheets()" py:strip="">
    <link rel="stylesheet" type="text/css" 
          href="/static/stylesheets/mollio.css" media="screen" />
    <link rel="stylesheet" type="text/css" 
          href="/static/stylesheets/mollio_print.css" media="print" />
    <!--[if lte IE 6]>
    <link rel="stylesheet" type="text/css" href="/static/stylesheets/mollio_ie.css" />
    <![endif]-->
</block>


<block py:def="default_ecmascripts()" py:strip="">
    <script type="text/javascript" 
            src="/static/mochikit/MochiKit.js" />
    <script type="text/javascript" 
            src="/static/ecmascripts/mollio.js" />
</block>


<div py:def="site_name()" id="site-name">
    New Application
</div>


<div py:def="site_search()" id="search">
<!-- site search is diabled in the default installation
    <form action="">
    <label for="searchsite">Site Search:</label>
    <input id="searchsite" name="searchsite" type="text" />
    <input type="submit" value="Go" class="f-submit" />
    </form>
-->
</div>


<ul py:def="site_nav()" id="nav">
    <li class="first active"><a href="/">Home</a></li>
    <li class=""><a href="/documentation">Documentation</a>
        <ul>
	<li class="first"><a href="/documentation#introduction">Introduction</a></li>
	<li class=""><a href="/documentation#programs">Writing Programs (Controllers)</a></li>
	<li><a href="/documentation#templates">Writing Templates (Views)</a></li>
	<li><a href="/documentation#caching">Caching</a></li>
	<li><a href="/documentation#sessions">Sessions</a></li>
	<li><a class="last" href="/documentation#forms">Forms</a></li>
	</ul>
    </li>
    <li><a href="/community">Community</a>
        <ul>
	<li class="first"><a href="/community">Mailing List</a></li>
	<li><a href="/community">Wiki</a></li>
	<li class="last"><a href="/commmunity">Trac</a></li>
	</ul>
    </li>

</ul>



<ul py:def="secondary_nav()" id="nav-secondary">
    <li class="first"><a href="/">Home</a></li>
    <li><a href="/documentation">Documentation</a></li>
    <li class="active"><a href="/community">Community</a>
        <ul>
        <li class="first"><a href="/community#mailinglist">Mailing List</a></li>
        <li><a href="/community#wiki">Wiki</a></li>
	<li class="active last"><a href="/community#trac">Trac</a></li>
	</ul>
    </li>
    <li><a href="#">Flying Sheep</a></li>
    <li><a href="#">Crunchy Frog</a></li>
    <li class="last"><a href="#">Musical Mice</a></li>
</ul>


<block py:def="extra_stylesheets()" py:strip="">
</block>

<block py:def="extra_ecmascripts()" py:strip="">
    <script type="text/javascript">
    </script>
</block>


<div py:def="footer()" id="footer">
    <p>A note here to go in the footer</p>
    <p><a href="#">Contact Us</a> | <a href="#">Privacy</a> | <a href="#">Links</a></p>
</div>


<div py:def="breadcrumbs()" id="breadcrumb">
<!-- breadcrumbs are disabled in the default installation
    <a href="/">Home</a> / <a href="/">Section Name</a> / <strong>Page Name</strong>
-->
</div>


<div py:def="heading_examples()">
    <?python value = lipsum_sentances[4][:-1].title() ?>
    <h1>Heading Examples</h1>
    <hr />

    <h1>&lt;h1&gt;${value}&lt;/h1&gt;</h1>
    <h2>&lt;h2&gt;${value}&lt;/h2&gt;</h2>
    <h3>&lt;h3&gt;${value}&lt;/h3&gt;</h3>
    <h4>&lt;h4&gt;${value}&lt;/h4&gt;</h4>
    <h5>&lt;h5&gt;${value}&lt;/h5&gt;</h5>
    <h6>&lt;h6&gt;${value}&lt;/h6&gt;</h6>
    <hr />
</div>

<div py:def="paragraph_examples()">
    <h1>Paragraph Examples</h1>
    <h2>Normal Paragraph</h2>
    <p>${lipsum}</p> 
    <hr />

    <div py:for="class_name in ['highlight', 'subdued', 'error', 'success', 'caption']"
	 py:strip="">
    <h2>Paragraph with class="${class_name}"</h2>
    <p class="${class_name}">${lipsum}</p> 
    <hr />
    </div>

    <h2>Paragaph with &lt;small&gt; Tags</h2>
    <p><small>${lipsum}</small></p>
    <hr />
    
    <h2>Paragraph with &lt;em&gt; Tags</h2>
    <p><em>${lipsum}</em></p>
    <hr />

    <h2>Paragraph with &lt;strong&gt; Tags</h2>
    <p><strong>${lipsum}</strong></p>
    <hr />
</div>


<div py:def="featurebox_examples()">
    <h1>Featurebox Examples</h1>
    <div class="featurebox">
        <h3>&lt;h3&gt;Heading inside a "featurebox" div&lt;h3/&gt;</h3>
        <p>${lipsum}</p>
    </div>
    <hr />

    <div class="featurebox2">
        <h3>&lt;h3&gt;Heading inside a "featurebox2" div&lt;h3/&gt;</h3>
        <p>${lipsum}</p>
    </div>
    <hr />
</div>

<div py:def="list_examples()">
    <h1>List Examples</h1>

    <h3>List of Links</h3>
    <ul>
	<li py:for="fruit in fruits"><a href="#">${fruit} Link</a></li>
    </ul>
    <hr />

    <h3>Paragraph and Related Links</h3>
    <p>${lipsum}</p>

    <ul class="related">
	<li py:for="fruit in fruits"><a href="#">${fruit} Related Link</a></li>
    </ul>
    <hr />

    <h3>Unordered List</h3>
    <ul>
	<li py:for="fruit in fruits">${fruit}</li>
    </ul>
    <hr />

    <h3>Ordered List</h3>
    <ol>
	<li py:for="fruit in fruits">${fruit}</li>
    </ol>
    <hr />

    <h3>Definition List</h3>

    <dl>
	<dt>Definition Term</dt>
	<dd>Definition - ${lipsum}</dd>
	<dt>Definition Term</dt>
	<dd>Definition - ${lipsum}</dd>
    </dl>
    <hr />
</div>


<div py:def="headline_examples()">
    <h1>Headline Examples</h1>

    <h4><span class="date">29 July 2005</span> Headline and associate
    teaser</h4>
    <p>${lipsum[:130]}.<a href="#"
    class="morelink" title="Headline and associate
    teaser">More <span>about: Headline and associate teaser</span></a>
    </p>


    <h4><span class="date">29 July 2005</span> Headline and associate
    teaser and thumbnail</h4>
    <p>
        <span class="thumbnail">
        <a href="#"><img src="/static/images/thumb_100wide.gif" alt="Demo" width="100" height="75" /></a></span>
	${lipsum}
        <a href="#" class="morelink" title="Headline
        and associate teaser">More <span>about: Headline and associate
        teaser</span></a>
    </p>

    <hr />
</div>


<div py:def="pagination_example()">
    <h1>Pagination Example</h1>
    <div class="pagination">
	<p>
	    <span><strong>Previous</strong></span> 
	    <span>1</span> <a href="#">2</a> 
	    <a href="#">3</a> 
	    <a href="#">4</a> 
	    <a href="#">5</a> 
	    <a href="#"><strong>Next</strong></a>
	</p>
	<h4>Page 1 of 5</h4>
    </div>
    <hr />
</div>


<div py:def="search_example()">
    <h1>Search Results Example</h1>
    <div id="resultslist-wrap">
    <ol>
        <li>
	    <dl>
	    <dt><a href="#">${lipsum_sentances[0]}</a></dt>
	    <dd class="desc">${lipsum_sentances[1]}</dd>
	    <dd class="filetype">HTML</dd>
	    <dd class="date">22 April 2005</dd>
	    </dl>
	</li>
	<li>
	    <dl>
            <dt><a href="#">${lipsum_sentances[2]}</a></dt>
	    <dd class="desc">${lipsum}</dd>
	    <dd class="filetype">HTML</dd>
	    <dd class="date">22 April 2005</dd>
	    </dl>
	</li>
	<li>
	    <dl>
	    <dt><a href="#">${lipsum_sentances[3]}</a></dt>
	    <dd class="desc">${lipsum_sentances[4]}</dd>
	    <dd class="filetype">PDF</dd>
	    <dd class="date">22 April 2005</dd>
	    </dl>
	</li>
	<li>
	    <dl>
	    <dt><a href="#">${lipsum_sentances[5]}</a></dt>
	    <dd class="desc">${lipsum_sentances[6]}</dd>
	    <dd class="filetype">ODF</dd>
	    <dd class="date">22 April 2005</dd>
	    </dl>
	</li>
    </ol>
    </div>
    <hr />
</div>

<div py:def="table_example()">
    <h1>Table Example</h1>
    <table class="table1">
	<thead>
	    <tr>
		<th colspan="3">Table Heading</th>
	    </tr>
	</thead>
	<tbody>
	    <tr>
		<th>Col 1</th>
		<th>Col 2</th>
		<th>Col 3</th>
	    </tr>
	    <tr>
		<th class="sub">Sub head 1</th>
		<td>209385</td>
		<td>45</td>
	    </tr>
	    <tr>
		<th class="sub">Sub head 2</th>
		<td>4577</td>
		<td>22</td>
	    </tr>
	    <tr>
		<th class="sub">Sub head 3</th>
		<td>69765</td>
		<td>75</td>
	    </tr>
	</tbody>
    </table>
    <hr />
</div>			

<div py:def="calendar_example()">
    <h1>Calendar Example</h1>
    <?python
	 import time, calendar
	 now = time.localtime()
	 month = now[1]
	 month_name = calendar.month_name[month]
	 year = now[0]
    ?>
    <table summary="Calendar for ${month_name} ${year}" class="table1 calendar">

	<thead>
	    <tr><th colspan="7">${month_name} ${year}</th></tr>
	    <tr><th py:for="dayname in calendar.day_abbr[:]">${dayname}</th></tr>
	</thead>
	<tbody>
	    <tr py:for="week in calendar.monthcalendar(year, month)">
		<td py:for="d in week">${d or ''}</td>
	    </tr>
	</tbody>
    </table>
    <hr />
</div>


<div py:def="form_example()">
    <h1>Form Example</h1>

    <form action="/" method="post" class="f-wrap-1">
	<div class="req"><b>*</b> Indicates required field</div>
	<fieldset>
	    <h3>Form title here</h3>

	    <label for="firstname"><b><span class="req">*</span>First name:</b>
		<input id="firstname" name="firstname" type="text" class="f-name" tabindex="1" /><br />
	    </label>
	    
	    <label for="lastname"><b><span class="req">*</span>Last name:</b>
		<input id="lastname" name="lastname" type="text" class="f-name" tabindex="2" /><br />
	    </label>
			
	    <label for="emailaddress"><b><span class="req">*</span>Email Address:</b>
		<input id="emailaddress" name="emailaddress" type="text" class="f-email" tabindex="3" /><br />
	    </label>
			
	    <label for="enquiry"><b>Enquiry Type:</b>
		<select id="enquiry" name="enquiry" tabindex="4">
		    <option>Select...</option>
		    <option>c nulla. Fusce tincidu</option>
		    <option>Maecenas digniss</option>
		    <option>tincidunt arcu eget sapien</option>
		</select>
		<br />
	    </label>
			
	    <fieldset class="f-checkbox-wrap">
		<b>Colour:</b>
		<fieldset>
		    <label for="blue">
			<input id="blue" type="checkbox" name="checkbox" value="checkbox" class="f-checkbox" tabindex="5" />
			sit amet, consectetu
		    </label>
				
		    <label for="green">
			<input id="green" type="checkbox" name="checkbox2" value="checkbox" class="f-checkbox" tabindex="6" />
			c nulla. Fusce tincidu
		    </label>
				
		    <label for="yellow">
			<input id="yellow" type="checkbox" name="checkbox3" value="checkbox" class="f-checkbox" tabindex="7" />
			tincidunt arcu eget 
		    </label>
		</fieldset>
	    </fieldset> 
			
	    <fieldset class="f-radio-wrap">
		<b>Country:</b>
		<fieldset>
		    <label for="australia">
			<input id="australia" type="radio" name="radio" value="Australia" class="f-radio" tabindex="8" />
			Australia
		    </label>

		    <label for="newzealand">
			<input id="newzealand" type="radio" name="radio" value="New Zealand" class="f-radio" tabindex="9" />
			New Zealand
		    </label>
				
		    <label for="antarctica">
			<input id="antarctica" type="radio" name="radio" value="Antarctica" class="f-radio" tabindex="10" />
			Antarctica
		    </label>
		</fieldset>
	    </fieldset>
			
	    <label for="comments"><b>Comments:</b>
		<textarea id="comments" name="comments" class="f-comments" rows="6" cols="20" tabindex="11"></textarea><br />
	    </label>
		
	    <div class="f-submit-wrap">
		<input type="submit" value="Submit" class="f-submit" tabindex="12" /><br />
	    </div>
	</fieldset>
    </form>
</div>


<div py:def="poweredby" id="poweredby">
    <a href="http://www.cleverharold.org/">
	<img src="/static/images/logo.gif" alt="Logo"  />
    </a>
</div>



<div py:def="sidebar()" id="sidebar">
    <div class="featurebox">
	<h3>Side Bar</h3>
	<p> This is the sidebar.  You can redefine it with a template
	    function "sidebar()", or you can change to a layout that
	    doesn't use it.
	</p>
    </div>

    <div class="featurebox">
	<h3>Clever Harold 0.1 Released</h3>
	<p>
	    Clever Harold makes web development faster, simpler, and well, more 
	    clever.  Clever Harold doesn't dance, and doesn't expect you to do
	    one just to write web apps.
        </p>

	<p> Visit the <a href="http://www.cleverharold.org/">Clever
	    Harold web site</a> for more information.  (But you're
	    already running a Clever Harold application, so chances
	    are you've been there at least once.  Go back, maybe
	    something has changed.)
	</p>

    </div>


</div>


<div py:def="main()" id="main">
This main() is empty.
</div>

<div py:def="full_example()">
    <h1>All Mollio HTML Examples</h1>
    <div py:replace="heading_examples()" />
    <div py:replace="paragraph_examples()" />
    <div py:replace="featurebox_examples()" />
    <div py:replace="list_examples()" />
    <div py:replace="headline_examples()" />
    <div py:replace="pagination_example()" />
    <div py:replace="search_example()" />
    <div py:replace="table_example()" />
    <div py:replace="calendar_example()" />
    <div py:replace="form_example()" />
</div>

</html>
