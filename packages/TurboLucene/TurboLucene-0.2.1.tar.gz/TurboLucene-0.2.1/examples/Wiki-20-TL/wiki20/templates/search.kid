<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml/DTD/xhtml-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Search - 20 Minute Wiki</title>
</head>
<body>
    <div id="main_content">
        <div style="float:right; width: 10em">
            Viewing Search
            <br/>
            You can return to the <a href="/">FrontPage</a>.
            <br/>
            <div py:replace="search_form(dict(query=query), action='search')">
                Search form goes here.
            </div>
        </div>

        <h1>Search</h1>
        <p py:if="not results">
            Sorry, no pages match
            "<span py:replace="query">Query goes here</span>".
        </p>
        <ul py:if="results">
            <li py:for="page in results">
                <a href="${tg.url('/' + page.pagename)}"
                    py:content="page.pagename">Pagename</a>
            </li>
        </ul>
    </div>
</body>
</html>
