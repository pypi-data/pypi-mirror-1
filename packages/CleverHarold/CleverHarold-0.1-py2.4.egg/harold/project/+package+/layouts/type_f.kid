<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
    <title py:replace="title()" />
    <meta py:replace="default_stylesheets()" />
    <meta py:replace="default_ecmascripts()" />
</head>

<body id="type-f">
    <div id="wrap">

        <div id="header">
            <div py:replace="site_name()" />
            <div py:replace="site_search()" />
            <div py:replace="site_nav()" />
        </div>

	
	<div id="content-wrap">
            <div id="utility">
		<div py:replace="secondary_nav()" />
            </div>

            <div id="content">
	        <div py:replace="breadcrumbs()" />
	        <div py:replace="main()" />
		<div py:replace="footer()" />
	    </div>
	    <div py:replace="sidebar()" />
            <div py:replace="poweredby()" />
		

		
	</div>
	
    </div>
</body>
</html>
