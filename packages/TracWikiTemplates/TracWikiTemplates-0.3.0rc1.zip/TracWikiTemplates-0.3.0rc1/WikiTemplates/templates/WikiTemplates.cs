<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>

<div id="ctxtnav" class="nav">
 <h2>Wiki Navigation</h2>
 <ul><?cs
  if:templates.action == "diff" ?>
   <li class="first"><?cs
     if:len(chrome.links.prev) ?> &larr; 
      <a class="prev" href="<?cs var:chrome.links.prev.0.href ?>" title="<?cs
       var:chrome.links.prev.0.title ?>">Previous Change</a><?cs
     else ?>
      <span class="missing">&larr; Previous Change</span><?cs
     /if ?>
   </li>
   <li><a href="<?cs var:templates.history_href ?>">Template History</a></li>
   <li class="last"><?cs
     if:len(chrome.links.next) ?>
      <a class="next" href="<?cs var:chrome.links.next.0.href ?>" title="<?cs
       var:chrome.links.next.0.title ?>">Next Change</a> &rarr; <?cs
     else ?>
      <span class="missing">Next Change &rarr;</span><?cs
     /if ?>
   </li><?cs
  elif:templates.action == "history" ?>
   <li class="last"><a href="<?cs var:templates.current_href ?>">View Latest Version</a></li><?cs
  else ?>
   <li class="last"><a href="<?cs var:templates.last_change_href ?>">Last Change</a></li><?cs 
  /if ?>
 </ul>
 <hr />
</div>

<div id="content" class="wiki">

 <?cs if templates.action == "delete" ?><?cs 
  if:templates.version - templates.old_version > 1 ?><?cs
   set:first_version = templates.old_version + 1 ?><?cs
   set:version_range = "versions "+first_version+" to "+templates.version+" of " ?><?cs
   set:delete_what = "those versions" ?><?cs
  elif:templates.version ?><?cs
   set:version_range = "version "+templates.version+" of " ?><?cs
   set:delete_what = "this version" ?><?cs
  else ?><?cs
   set:version_range = "" ?><?cs
   set:delete_what = "template" ?><?cs
  /if ?>
  <h1>Delete <?cs var:version_range ?><a href="<?cs
    var:templates.current_href ?>"><?cs var:templates.page_name ?></a> template</h1>
  <form action="<?cs var:templates.current_href ?>" method="post">
   <input type="hidden" name="action" value="delete" />
   <p><strong>Are you sure you want to <?cs
    if:!?templates.version ?>completely <?cs 
    /if ?>delete <?cs var:version_range ?>this template?</strong><br /><?cs
   if:templates.only_version ?>
    This is the only version the template, so the template will be removed
    completely!<?cs
   /if ?><?cs
   if:?templates.version ?>
    <input type="hidden" name="version" value="<?cs var:templates.version ?>" /><?cs
   /if ?><?cs
   if:templates.old_version ?>
    <input type="hidden" name="old_version" value="<?cs var:templates.old_version ?>" /><?cs
   /if ?>
   This is an irreversible operation.</p>
   <div class="buttons">
    <input type="submit" name="cancel" value="Cancel" />
    <input type="submit" value="Delete <?cs var:delete_what ?>" />
   </div>
  </form>
 
 <?cs elif:templates.action == "diff" ?>
  <h1>Changes <?cs
    if:templates.old_version ?>between 
     <a href="<?cs var:templates.current_href ?>?version=<?cs var:templates.old_version?>">Version <?cs var:templates.old_version?></a> and <?cs
    else ?>from <?cs
    /if ?>
    <a href="<?cs var:templates.current_href ?>?version=<?cs var:templates.version?>">Version <?cs var:templates.version?></a> of 
    <a href="<?cs var:templates.current_href ?>"><?cs var:templates.page_name ?></a></h1>
  <form method="post" id="prefs" action="<?cs var:templates.current_href ?>">
   <div>
    <input type="hidden" name="action" value="diff" />
    <input type="hidden" name="version" value="<?cs var:templates.version ?>" />
    <input type="hidden" name="old_version" value="<?cs var:templates.old_version ?>" />
    <label>View differences <select name="style">
     <option value="inline"<?cs
       if:diff.style == 'inline' ?> selected="selected"<?cs
       /if ?>>inline</option>
     <option value="sidebyside"<?cs
       if:diff.style == 'sidebyside' ?> selected="selected"<?cs
       /if ?>>side by side</option>
    </select></label>
    <div class="field">
     Show <input type="text" name="contextlines" id="contextlines" size="2"
       maxlength="3" value="<?cs var:diff.options.contextlines ?>" />
     <label for="contextlines">lines around each change</label>
    </div>
    <fieldset id="ignore">
     <legend>Ignore:</legend>
     <div class="field">
      <input type="checkbox" id="blanklines" name="ignoreblanklines"<?cs
        if:diff.options.ignoreblanklines ?> checked="checked"<?cs /if ?> />
      <label for="blanklines">Blank lines</label>
     </div>
     <div class="field">
      <input type="checkbox" id="case" name="ignorecase"<?cs
        if:diff.options.ignorecase ?> checked="checked"<?cs /if ?> />
      <label for="case">Case changes</label>
     </div>
     <div class="field">
      <input type="checkbox" id="whitespace" name="ignorewhitespace"<?cs
        if:diff.options.ignorewhitespace ?> checked="checked"<?cs /if ?> />
      <label for="whitespace">White space changes</label>
     </div>
    </fieldset>
    <div class="buttons">
     <input type="submit" name="update" value="Update" />
    </div>
   </div>
  </form>
  <dl id="overview">
   <dt class="property author">Author:</dt>
   <dd class="author"><?cs
    if:templates.num_changes > 1 ?><em class="multi">(multiple changes)</em><?cs
    else ?><?cs var:templates.author ?> <span class="ipnr">(IP: <?cs
     var:templates.ipnr ?>)</span><?cs
    /if ?></dd>
   <dt class="property time">Timestamp:</dt>
   <dd class="time"><?cs
    if:templates.num_changes > 1 ?><em class="multi">(multiple changes)</em><?cs
    elif:templates.time ?><?cs var:templates.time ?> (<?cs var:templates.time_delta ?> ago)<?cs
    else ?>--<?cs
    /if ?></dd>
   <dt class="property message">Comment:</dt>
   <dd class="message"><?cs
    if:templates.num_changes > 1 ?><em class="multi">(multiple changes)</em><?cs
    else ?><?cs var:templates.comment ?><?cs /if ?></dd>
  </dl>
  <div class="diff">
   <div id="legend">
    <h3>Legend:</h3>
    <dl>
     <dt class="unmod"></dt><dd>Unmodified</dd>
     <dt class="add"></dt><dd>Added</dd>
     <dt class="rem"></dt><dd>Removed</dd>
     <dt class="mod"></dt><dd>Modified</dd>
    </dl>
   </div>
   <ul class="entries">
    <li class="entry">
     <h2><?cs var:templates.page_name ?></h2><?cs
      if:diff.style == 'sidebyside' ?>
      <table class="sidebyside" summary="Differences">
       <colgroup class="l"><col class="lineno" /><col class="content" /></colgroup>
       <colgroup class="r"><col class="lineno" /><col class="content" /></colgroup>
       <thead><tr>
        <th colspan="2">Version <?cs var:templates.old_version ?></th>
        <th colspan="2">Version <?cs var:templates.version ?></th>
       </tr></thead><?cs
       each:change = templates.diff ?><?cs
        call:diff_display(change, diff.style) ?><?cs
       /each ?>
      </table><?cs
     else ?>
      <table class="inline" summary="Differences">
       <colgroup><col class="lineno" /><col class="lineno" /><col class="content" /></colgroup>
       <thead><tr>
        <th title="Version <?cs var:templates.old_version ?>">v<?cs
          var:templates.old_version ?></th>
        <th title="Version <?cs var:templates.version ?>">v<?cs
          var:templates.version ?></th>
        <th>&nbsp;</th>
       </tr></thead><?cs
       each:change = templates.diff ?><?cs
        call:diff_display(change, diff.style) ?><?cs
       /each ?>
      </table><?cs
     /if ?>
    </li>
   </ul><?cs
   if:trac.acl.TEMPLATES_DELETE && 
    (len(templates.diff) == 0 || templates.version == templates.latest_version) ?>
    <form method="get" action="<?cs var:templates.current_href ?>">
     <input type="hidden" name="action" value="delete" />
     <input type="hidden" name="version" value="<?cs var:templates.version ?>" />
     <input type="hidden" name="old_version" value="<?cs var:templates.old_version ?>" />
     <input type="submit" name="delete_version" value="Delete <?cs
     if:templates.version - templates.old_version > 1 ?> version <?cs 
      var:templates.old_version+1 ?> to <?cs 
     /if ?>version <?cs var:templates.version ?>" />
    </form><?cs
   /if ?>
  </div>

 <?cs elif templates.action == "history" ?>
  <h1>Change History of <a href="<?cs var:templates.current_href ?>"><?cs
    var:templates.page_name ?></a></h1>
  <?cs if:len(templates.history) ?><form class="printableform" method="get" action="">
   <input type="hidden" name="action" value="diff" />
   <div class="buttons">
    <input type="submit" value="View changes" />
   </div>
   <table id="wikihist" class="listing" summary="Change history">
    <thead><tr>
     <th class="diff"></th>
     <th class="version">Version</th>
     <th class="date">Date</th>
     <th class="author">Author</th>
     <th class="comment">Comment</th>
    </tr></thead>
    <tbody><?cs each:item = templates.history ?>
     <tr class="<?cs if:name(item) % #2 ?>even<?cs else ?>odd<?cs /if ?>">
      <td class="diff"><input type="radio" name="old_version" value="<?cs
        var:item.version ?>"<?cs
        if:name(item) == 1 ?> checked="checked"<?cs
        /if ?> /> <input type="radio" name="version" value="<?cs
        var:item.version ?>"<?cs
        if:name(item) == 0 ?> checked="checked"<?cs
        /if ?> /></td>
      <td class="version"><a href="<?cs
        var:item.url ?>" title="View this version"><?cs
        var:item.version ?></a></td>
      <td class="date"><?cs var:item.time ?></td>
      <td class="author" title="IP-Address: <?cs var:item.ipaddr ?>"><?cs 
        var:item.author ?></td>
      <td class="comment"><?cs var:item.comment ?></td>
     </tr>
    <?cs /each ?></tbody>
   </table><?cs
   if:len(templates.history) > #10 ?>
    <div class="buttons">
     <input type="submit" value="View changes" />
    </div><?cs
   /if ?>
  </form><?cs /if ?>
 
 <?cs else ?>
  <!-- Include form to create a new template -->
  <?cs if:templates.showform == 1 && templates.action == "view" && trac.acl.TEMPLATES_CREATE ?>
   <form id="prefs" method="post" action="<?cs var:templates_base_url ?>">
    <div>
     <fieldset>
     <center><p><strong>Create a New Template</strong></p></center>
      <label>Name: <input type="hidden" name="action" value="create"></label>
      <input id="new_tpl_name" name="new_tpl_name" type="text" size="20">
    </div>
    <div class="buttons">
     <input value="Create" type="submit">
    </div>
    </fieldset>
   </form>
  <?cs /if ?>
  <!-- End Of - Include form to create a new template -->
  <?cs if templates.action == "edit" || templates.action == "preview" || templates.action == "collision" ?>
   <h1>Editing "<?cs var:templates.page_name ?>"</h1><?cs
    if templates.action == "preview" ?>
     <table id="info" summary="Revision info"><tbody><tr>
       <th scope="col">
        Preview of future version <?cs var:$templates.version+1 ?> (modified by <?cs var:templates.author ?>)
       </th></tr><tr>
       <td class="message"><?cs var:templates.comment_html ?></td>
      </tr>
     </tbody></table>
     <fieldset id="preview">
      <legend>Preview (<a href="#edit">skip</a>)</legend>
        <div class="wikipage"><?cs var:templates.page_html ?></div>
     </fieldset><?cs
     elif templates.action =="collision"?>
     <div class="system-message">
       Sorry, this template has been modified by somebody else since you started 
       editing. Your changes cannot be saved.
     </div><?cs
    /if ?>
   <form id="edit" action="<?cs var:templates.current_href ?>" method="post">
    <fieldset class="iefix">
     <input type="hidden" name="action" value="edit" />
     <input type="hidden" name="version" value="<?cs var:templates.version ?>" />
     <input type="hidden" id="scroll_bar_pos" name="scroll_bar_pos" value="<?cs
       var:templates.scroll_bar_pos ?>" />
     <div id="rows">
      <label for="editrows">Adjust edit area height:</label>
      <select size="1" name="editrows" id="editrows" tabindex="43"
        onchange="resizeTextArea('text', this.options[selectedIndex].value)"><?cs
       loop:rows = 8, 42, 4 ?>
        <option value="<?cs var:rows ?>"<?cs
          if:rows == templates.edit_rows ?> selected="selected"<?cs /if ?>><?cs
          var:rows ?></option><?cs
       /loop ?>
      </select>
     </div>
     <p><textarea id="text" class="wikitext" name="text" cols="80" rows="<?cs
       var:templates.edit_rows ?>">
<?cs var:templates.page_source ?></textarea></p>
     <script type="text/javascript">
       var scrollBarPos = document.getElementById("scroll_bar_pos");
       var text = document.getElementById("text");
       addEvent(window, "load", function() {
         if (scrollBarPos.value) text.scrollTop = scrollBarPos.value;
       });
       addEvent(text, "blur", function() { scrollBarPos.value = text.scrollTop });
     </script>
    </fieldset>
    <div id="help">
     <b>Note:</b> See <a href="<?cs var:$trac.href.wiki
?>/WikiFormatting">WikiFormatting</a> and <a href="<?cs var:$trac.href.wiki
?>/TracWiki">TracWiki</a> for help on editing wiki content.
    </div>
    <fieldset id="changeinfo">
     <legend>Change information</legend>
     <?cs if:trac.authname == "anonymous" ?>
      <div class="field">
       <label>Your email or username:<br />
       <input id="author" type="text" name="author" size="30" value="<?cs
         var:templates.author ?>" /></label>
      </div>
     <?cs /if ?>
     <div class="field">
      <label>Comment about this change (optional):<br />
      <input id="comment" type="text" name="comment" size="60" value="<?cs
        var:templates.comment?>" /></label>
     </div><br />
     <?cs if trac.acl.TEMPLATES_ADMIN ?>
      <div class="options">
       <label><input type="checkbox" name="readonly" id="readonly"<?cs
         if templates.readonly == "1"?>checked="checked"<?cs /if ?> />
       Page is read-only</label>
      </div>
     <?cs /if ?>
    </fieldset>
    <div class="buttons"><?cs
     if templates.action == "collision" ?>
      <input type="submit" name="preview" value="Preview" disabled="disabled" />&nbsp;
      <input type="submit" name="save" value="Submit changes" disabled="disabled" />&nbsp;
     <?cs else ?>
      <input type="submit" name="preview" value="Preview" accesskey="r" />&nbsp;
      <input type="submit" name="save" value="Submit changes" />&nbsp;
     <?cs /if ?>
     <input type="submit" name="cancel" value="Cancel" />
    </div>
    <script type="text/javascript" src="<?cs
      var:htdocs_location ?>js/wikitoolbar.js"></script>
   </form>
  <?cs /if ?>
  <?cs if templates.action == "view" ?>
   <?cs if:templates.comment_html ?>
    <table id="info" summary="Revision info"><tbody><tr>
      <th scope="col">
       Version <?cs var:templates.version ?> (modified by <?cs var:templates.author ?>, <?cs var:templates.age ?> ago)
      </th></tr><tr>
      <td class="message"><?cs var:templates.comment_html ?></td>
     </tr>
    </tbody></table>
   <?cs /if ?>
   <div class="wikipage">
    <div id="searchable"><?cs var:templates.page_html ?></div>
   </div>
   <?cs if:len(templates.attachments) ?>
    <h3 id="tkt-changes-hdr">Attachments</h3>
    <ul class="tkt-chg-list"><?cs
     each:attachment = templates.attachments ?><li class="tkt-chg-change"><a href="<?cs
      var:attachment.href ?>"><?cs
      var:attachment.filename ?></a> (<?cs var:attachment.size ?>) -<?cs
      if:attachment.description ?><q><?cs var:attachment.description ?></q>,<?cs
      /if ?> added by <?cs var:attachment.author ?> on <?cs
      var:attachment.time ?>.</li><?cs
     /each ?>
    </ul>
  <?cs /if ?>

  <!-- Include Real Preview -->
    <?cs if:len(templates) ?>
     <?cs each:preview=previews ?>
      <P>
      <FIELDSET class="tplprev">
        <LEGEND class="tplprev" ALIGN="right">
          Template Preview [
          <a href="<?cs var:templates_base_url ?>/<?cs var:preview.name ?>">
          <?cs var:preview.name ?></a> ]
        </LEGEND><P>
        <?cs var:preview.contents ?>
      </FIELDSET><P>
     <?cs /each ?>
    <?cs /if ?>
  <!-- End Of Template Real Preview -->

  <?cs if templates.action == "view" && (trac.acl.TEMPLATES_MODIFY || trac.acl.TEMPLATES_DELETE)
      && (templates.readonly == "0" || trac.acl.TEMPLATES_ADMIN) ?>
   <div class="buttons"><?cs
    if:trac.acl.TEMPLATES_MODIFY ?>
     <form method="get" action="<?cs var:templates.current_href ?>"><div>
      <input type="hidden" name="action" value="edit" />
	  <?cs if:templates.page_name == 'TemplatesIndex' ?>
	    <input type="submit" value="Edit the templates index"  accesskey="e" />
	  <?cs else ?>
        <input type="submit" value="<?cs if:templates.exists ?>Edit<?cs
          else ?>Create<?cs /if ?> this template" accesskey="e" />
	  <?cs /if ?>
     </div></form><?cs
     if:templates.exists ?>
      <form method="get" action="<?cs var:templates.attach_href ?>"><div>
       <input type="hidden" name="action" value="new" />
       <input type="submit" value="Attach file" />
      </div></form><?cs
     /if ?><?cs
    /if ?><?cs
    if:templates.exists && trac.acl.TEMPLATES_DELETE ?>
     <form method="get" action="<?cs var:templates.current_href ?>"><div id="delete">
      <input type="hidden" name="action" value="delete" />
      <input type="hidden" name="version" value="<?cs var:templates.version ?>" /><?cs
      if:templates.version == templates.latest_version ?>
       <input type="submit" name="delete_version" value="Delete this version" /><?cs
      /if ?>
	  <?cs if:templates.page_name != 'TemplatesIndex' ?>
	    <input type="submit" value="Delete template" />
	  <?cs /if ?>
     </div></form>
    <?cs /if ?>
   </div>
  <?cs /if ?>
  <script type="text/javascript">
   addHeadingLinks(document.getElementById("searchable"), "Link to this section");
  </script>
 <?cs /if ?>
 <?cs /if ?>
</div>

<?cs include "footer.cs" ?>
