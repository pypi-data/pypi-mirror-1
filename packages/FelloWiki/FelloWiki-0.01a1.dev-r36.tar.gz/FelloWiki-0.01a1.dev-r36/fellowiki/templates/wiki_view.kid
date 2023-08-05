<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" 
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">

    <head>
        <title>${title}</title>
    </head>
    <body>
        <h1 class='page_name'><span py:replace="page_name">This is the page name</span></h1>
        <div class='main_content'><span py:replace="main_content">This ist the wiki page main content</span></div>
        <hr />
        <a href="${edit_link}" py:if="page_is_editable">edit this page</a>
    </body>
</html>
