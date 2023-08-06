<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <form action=";edit" method="post" stl:if="msgid">
    <input value="${messages_index}" name="messages_index" type="hidden"></input>
    <table>
      <tr>
        <th>
          Message ${messages_index} / ${messages_total} <br></br>  <a href="${messages_first}" title="Go to first message">&lt;&lt;</a>
          <a href="${messages_previous}" title="Go to previous message">&lt;</a>
          <a href="${messages_next}" title="Go to next message">></a>  <a href="${messages_last}" title="Go to last message">>></a>
        </th>
        <td>
          <textarea name="msgid" rows="8" cols="65" readonly="">${msgid}</textarea>
        </td>
      </tr>
      <tr>
        <th>
          Traducción
        </th>
        <td>
          <textarea name="msgstr" rows="8" cols="65">${msgstr}</textarea>
        </td>
      </tr>
      <tr>
        <th></th>
        <td>
          <input value="Change" class="button_ok" type="submit"></input>
        </td>
      </tr>
    </table>
  </form>

  <p stl:if="not msgid">
    There aren't messages.
  </p>

</stl:block>
