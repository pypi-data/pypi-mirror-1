<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <form action=";rename" method="post">
    <table style="margin-left: 20px; font-family: monospace;">
      <tr stl:repeat="item items">
        <td>
          <input value="${item/path}" name="paths" type="hidden"></input>
          ${item/path}
        </td>
        <td>
          ⇒ ${item/parent_path}<input value="${item/name}" name="new_names" style="font-family: monospace;" type="text"></input>
        </td>
      </tr>
    </table>
    <p><input value="Renombrar" class="button_rename" type="submit"></input></p>
  </form>

</stl:block>
