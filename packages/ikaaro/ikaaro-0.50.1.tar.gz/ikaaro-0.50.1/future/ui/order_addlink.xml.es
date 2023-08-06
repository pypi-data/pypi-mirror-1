<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">
  <head>
    <title>Insert link</title>
    <link rel="stylesheet" href="${style}" stl:repeat="style styles" type="text/css"></link>
    <script src="${script}" stl:repeat="script scripts" type="text/javascript"></script>
    <script type="text/javascript">
      $(document).ready(function() {
        tabme();
      })
    </script>
    <script type="text/javascript">
      function select_link(value) {
        var opener = window.opener;
        var form = opener.document.getElementById('autoform');
        var target = form.${target_id};
        if (target)
          target.value = value;
        window.close();
      }
      function select_uri() {
        var value = document.getElementById('uri').value;
        select_link(value);
      }
    </script>
    <style>
      #body {
        border-top: 20px solid #30569D;
        padding: 20px;
      }
      table.thumbs {
        border-collapse: collapse;
      }
      table.thumbs th,
      table.thumbs td {
        border: 2px solid #ccc;
      }
      dt a {
        white-space: nowrap;
      }
    </style>
  </head>

  <body>
    <div id="body">
      <!-- Message -->
      <div id="message" stl:if="message">Message: ${message}</div>

      <!-- Internal Link -->
      <div id="browse">
        <!-- Breadcrumbs -->
        <div id="maintitle">
          <div id="breadcrumbs" style="float: none;">
            <label>Localización:</label>
            <span stl:repeat="x bc/path">
              <a href="${x/url}" title="${x/title}">${x/short_title}</a> /
            </span>
          </div>
        </div>
        <br></br>
        <table cellspacing="1" width="100%" cellpadding="1" class="thumbs" border="0">
          <tr>
            <th>Select Resource</th>
          </tr>
          <tr>
            <td valign="top">
              <!-- Files and Folders to select -->
              <stl:block stl:repeat="item bc/items">
                <dl class="thumb">
                  <dt>
                    <img src="${item/icon}" width="48" title="${item/item_type}" alt="" height="48"></img>
                  </dt>
                  <dd>
                    <abbr title="${item/title}">${item/short_title}</abbr><br></br>  <a href="javascript:select_link('${item/path}')">Select</a>
                  </dd>
                </dl>
              </stl:block>
            </td>
          </tr>
        </table>
      </div>
    </div>
  </body>
</html>
