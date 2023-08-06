<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <!-- Batch -->
  ${batch}

  <table stl:repeat="item items" class="new_resource_thumb">
    <tr>
      <td style="width: 48px" valign="top">
        <a href="${item/url}"><img src="${item/icon}" alt=""></img></a>
      </td>
      <td valign="top">
        <a href="${item/url}">${item/title}</a>  <br></br> ${item/description}
      </td>
    </tr>
  </table>
  <div class="clear"></div>

</stl:block>
