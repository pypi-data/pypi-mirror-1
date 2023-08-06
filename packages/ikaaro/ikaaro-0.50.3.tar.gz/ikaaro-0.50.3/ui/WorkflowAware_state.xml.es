<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <p>
  Estado actual: <strong class="wf_${statename}">${state}</strong>
  </p>

  <form action=";edit_state" method="post">
    <dl>
      <dt>You can do the following actions:</dt>
      <dd stl:repeat="transition transitions">
        <input name="transition" type="radio" id="${transition/name}" value="${transition/name}"></input>
        <label for="${transition/name}">${transition/description}</label>
      </dd>
    </dl>
    <dl>
      <dt><label for="comments">Comments (optional):</label></dt>
      <dd>
        <textarea id="comments" cols="52" rows="7" name="comments"></textarea>
      </dd>
    </dl>
    <p>
      <input value="Change" class="button_ok" type="submit"></input>
    </p>
  </form>

  <h4>State History</h4>

  <p stl:if="not history">
    No history.
  </p>

  <table id="browse_list" stl:if="history">
    <thead>
      <tr>
        <th>Fecha</th>
        <th>Acción</th>
        <th>Por</th>
        <th>Comentarios</th>
      </tr>
    </thead>
    <tbody>
      <tr stl:repeat="transition history" class="${repeat/transition/even}">
        <td>${transition/date}</td>
        <td>${transition/title}</td>
        <td>${transition/user}</td>
        <td>${transition/comments}</td>
      </tr>
    </tbody>
  </table>

</stl:block>
