<h2>Navigation Add</h2>

<form id="addrole" class="addnew" method="post">
  <fieldset>
    <legend>Add New Item</legend>
    <div class="field">
      <label for="title">Title:</label>
      <input type="text" name="title" />
    </div>
    <div class="field">
      <label for="url">URL:</label>
      <input type="text" name="url" />
    </div>
    <div class="field">
      <label for="bar">Bar:</label>
      <select name="bar" />
        <option value="mainnav">Mainnav</option>
        <option value="metanav">Metanav</option>
      </select>
    </div>
    <p class="help">Add a new menu bar entry</p>
    <div class="buttons">
      <input type="submit" name="add" value="Add" />
    </div>
  </fieldeset>
</form>

<form method="post">
  <table class="listing">
    <thead>
      <tr>
        <th class="sel">&nbsp;</th>
        <th>Title</th>
        <th>URL</th>
      </tr>
    </thead>
    <?cs each:bar = navplus.items ?>
    <tr class="header">
      <th colspan="3"><?cs name:bar ?></th>
    </tr>
    <?cs each:item = bar ?>
    <tr>
      <td><input type="checkbox" name="sel" value="<?cs var:item.name ?>" /></td>
      <td><?cs var:item.title ?></td>
      <td><?cs var:item.url ?></td>
    </tr>
    <?cs /each ?>
    <?cs /each ?>
  </table>
  <div class="buttons">
    <input type="submit" name="remove" value="Remove selected items" />
  </div>
</form>