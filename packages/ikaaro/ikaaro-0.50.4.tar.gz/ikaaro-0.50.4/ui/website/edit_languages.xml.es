<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <!-- Edit Languages -->
  <fieldset>
    <legend>Edit the active languages</legend>
    <form id="browse_list" action="" method="post">
      <table summary="Configuration des langues">
        <thead>
          <tr>
            <th></th>
            <th>Nombre</th>
            <th>Código</th>
            <th>Default</th>
          </tr>
        </thead>
        <tbody>
          <tr stl:repeat="language active_languages" class="${repeat/language/even}">
            <td>
              <input class="checkbox" type="checkbox" name="codes" value="${language/code}"></input>
            </td>
            <td>${language/name}</td>
            <td>${language/code}</td>
            <td align="center">
              <stl:block stl:if="language/isdefault">Sí</stl:block>
            </td>
          </tr>
        </tbody>
      </table>
      <p>
        <input value="Change default" type="submit" name=";change_default_language" class="button_ok"></input>
        <input name=";remove_languages" type="submit" class="button_delete" value="Suprimir"></input>
      </p>
    </form>
  </fieldset>

  <br></br>

  <!-- Add Language -->
  <fieldset>
    <legend>Agregar otro idioma</legend>
    <form action="" method="post">
      <select id="new_language" name="code">
        <option value="">Elije un idioma</option>
        <option value="${language/code}" stl:repeat="language not_active_languages">${language/name}</option>
      </select>
      <input value="Agregar" type="submit" name=";add_language" class="button_ok"></input>
    </form>
  </fieldset>

</stl:block>
