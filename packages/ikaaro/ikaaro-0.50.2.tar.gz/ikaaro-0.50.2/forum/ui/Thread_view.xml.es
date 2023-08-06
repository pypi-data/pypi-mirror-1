<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <form action="." method="post">
    <table width="100%" id="forum_message_list">
      <colgroup>
        <col width="20%"/>
        <col width="80%"/>
      </colgroup>
      <tbody>
        <tr stl:repeat="message messages" class="${repeat/message/even}">
          <td class="forum_message_info" valign="top">
            <p class="forum_message_author">${message/author}</p>
            <p class="forum_message_date">${message/mtime}</p>
            <stl:block stl:if="editable">
              <a href="${message/link}/;edit">Editar</a>
              <stl:block stl:if="not repeat/message/start">
                <br></br>
                <input value="${message/name}" name="ids" type="checkbox"></input>
              </stl:block>
            </stl:block>
          </td>
          <td class="forum_message_body" valign="top">
            <p>${message/body}</p>
          </td>
        </tr>
      </tbody>
    </table>
    <p stl:if="editable">
      <input value="Suprimir" name=";remove" type="submit" class="button_delete" onclick="return confirm('${remove_message}');"></input>
    </p>
  </form>

  <a name="new_reply"></a>
  <form action="." method="post" stl:if="is_allowed_to_add">
    <hr/>
    <h3>Post a Reply</h3>
    ${rte}
    <p>
    <input value="Responder" name=";new_reply" class="button_ok" type="submit"></input>
    </p>
  </form>

</stl:block>
