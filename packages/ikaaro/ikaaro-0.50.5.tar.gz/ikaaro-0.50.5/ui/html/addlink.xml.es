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
      ${additional_javascript}
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

      <!-- tabs -->
      <p class="tabme">
        <a onclick="tabme_show(event, this)" href="#browse" stl:if="show_browse">Browse</a>  <a onclick="tabme_show(event, this)" href="#external" stl:if="show_external">External Link</a>  <a onclick="tabme_show(event, this)" href="#insert" stl:if="show_insert">Insert</a>  <a onclick="tabme_show(event, this)" href="#upload" stl:if="show_upload">Upload</a>
      </p>

      <!-- Message -->
      <div id="message" stl:if="message">Message: ${message}</div>

      <!-- Internal Link -->
      <div id="browse" stl:if="show_browse">
        <h3>Browse and link to a File from the workspace</h3>
        <!-- Breadcrumbs -->
        <div id="maintitle">
          <div id="breadcrumbs">
            <label>Localización:</label>
            <span stl:repeat="x bc/path">
              <a href="${x/url}" title="${x/title}">${x/short_title}</a> /
            </span>
          </div>
        </div>
        <table width="100%" cellspacing="1" cellpadding="1" class="thumbs" border="0">
          <tr>
            <th width="150">Inspeccionar el Contenido</th>
            <th>Select Resource</th>
          </tr>
          <tr>
            <td valign="top">
              <!-- Browse Folders -->
              <stl:block stl:repeat="item bc/items">
                <dl stl:if="item/is_folder">
                  <dt>
                    <a href="${item/url}" title="${item/title}"><img src="${item/icon}" width="16" alt="" height="16"></img> ${item/short_title}</a>
                  </dt>
                </dl>
              </stl:block>
            </td>
            <td valign="top">
              <!-- Files and Folders to select -->
              <stl:block stl:repeat="item bc/items">
                <dl class="thumb">
                  <dt>
                    <img src="${item/icon}" width="48" title="${item/item_type}" alt="" height="48"></img>
                  </dt>
                  <dd>
                    <abbr title="${item/title}">${item/short_title}</abbr><br></br>  <a href="javascript:select_element('${element_to_add}', '${item/path}', '${item/quoted_title}')"> Select </a>
                  </dd>
                </dl>
              </stl:block>
            </td>
          </tr>
        </table>
      </div>

      <!-- External Link -->
      <div id="external" stl:if="show_external">
        <h3>Type the URL of an external resource</h3>
        <form>
          <input id="uri" value="http://" name="uri" size="40" type="text"></input>
          <input value="Add" type="button" class="button_ok" onclick="select_element('${element_to_add}', $('#uri').val(), '');"></input>
        </form>
      </div>

      <!-- New Web or Wiki Page -->
      <div id="insert" stl:if="show_insert">
        <h3>Create a new page and link to it:</h3>
        <form action=";add_link#insert" method="post">
          <input value="${bc/target_path}" name="target_path" type="hidden"></input>
          <input value="${target_id}" name="target_id" type="hidden"></input>  <input value="${mode}" name="mode" type="hidden"></input>  <input name="title" size="40" type="text"></input>  <input value="" name="name" type="hidden"></input>
          <input value="Aceptar" class="button_ok" name=";add_resource" type="submit"></input>
        </form>
      </div>

      <!-- Upload and Link -->
      <div id="upload" stl:if="show_upload">
        <h3>Upload a file to the current folder and link to it:</h3>
        <form action=";add_link#upload" method="post" enctype="multipart/form-data">
          <input value="${bc/target_path}" name="target_path" type="hidden"></input>
          <input value="${target_id}" name="target_id" type="hidden"></input>  <input value="${mode}" name="mode" type="hidden"></input>  <input id="file" name="file" size="35" type="file"></input>  <br></br>
          <input value="Upload and Link" class="button_upload" name=";upload" type="submit"></input>
        </form>
      </div>
    </div>
  </body>
</html>
