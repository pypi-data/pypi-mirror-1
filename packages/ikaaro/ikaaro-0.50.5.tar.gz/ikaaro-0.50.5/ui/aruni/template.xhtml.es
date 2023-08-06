<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="${language}" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">
  <head>
    <title>${title}</title>
    <base href="${base_uri}"/>
    <!-- Meta -->
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type"></meta>
    <meta name="${meta/name}" lang="${meta/lang}" stl:repeat="meta meta_tags" content="${meta/content}"></meta>  <!-- CSS -->  <link rel="stylesheet" href="${style}" stl:repeat="style styles" type="text/css"></link>

    <!-- JavaScript -->
    <script src="${script}" stl:repeat="script scripts" type="text/javascript"></script>

    <!-- Icon -->
    <link rel="shortcut icon" href="${favicon_href}" type="${favicon_type}"></link>
  </head>

  <body>

    <!-- Header -->
    <div id="header">
      ${languages}
      <div id="top_menu">
        <stl:block stl:if="not user/info">
          <a href="${login}" id="top_menu_login">Log in</a>  <a href="/;register" id="top_menu_register" stl:if="user/joinisopen">Register</a>
        </stl:block>
        <stl:block stl:if="user/info">
          <a href="${user/info/home}" id="top_menu_profile">My Profile</a>  <a href="${logout}" id="top_menu_logout">Log out</a>
        </stl:block>
        <a href="/;site_search" id="top_menu_search">Search</a>  <a href="/;contact" id="top_menu_contact">Contact</a>
      </div>
    </div>

    <!-- Location & Views-->
    ${location}

    <!-- Body -->
    <div id="body">
      <h1 stl:if="page_title">${page_title}</h1>
      ${message}
      <table width="100%" cellpadding="0" border="0" cellspacing="0">
        <tr>
          <td id="content" valign="top">
            ${body}
          </td>
          <td id="right" valign="top">
            <stl:block stl:repeat="menu context_menus">${menu}<br></br></stl:block>
          </td>
        </tr>
      </table>
    </div>

    <!-- Footer -->
    <div id="footer">
      <a href="/;about">About</a>  <a href="/;credits">Credits</a>  <a href="/;license">License</a>
    </div>
  </body>
</html>
