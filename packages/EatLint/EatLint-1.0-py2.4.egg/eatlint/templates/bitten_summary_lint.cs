<h3>Code Lint</h3>
<table class="listing lint">
 <thead>
    <tr><th rowspan="2" class="file">File</th><th colspan="4" class="category">Problem Category Totals</th><th rowspan="2" class="total">Total</th></tr>
    <tr>
	<th class="category">Convention</th>
	<th class="category">Refactor</th>
	<th class="category">Warning</th>
	<th class="category">Error</th>
    </tr>
 </thead>

 <tbody><?cs
 each:item = data ?><tr><td class="file"><?cs
  if:item.href ?><a href="<?cs var:item.href ?>"><?cs var:item.file ?></a><?cs
  else ?><?cs var:item.file ?><?cs
  /if ?></td>
  
    <td class="category"><?cs var:item.category.convention ?></td>
    <td class="category"><?cs var:item.category.refactor ?></td>
    <td class="category"><?cs var:item.category.warning ?></td>
    <td class="category"><?cs var:item.category.error ?></td>
    <td class="category"><?cs var:item.lines ?></td>

  </tr><?cs
 /each ?></tbody>
 <tbody class="totals"><tr>
    <th>Total (in <?cs var:totals.files ?> files)</th>
  
    <td class="category total"><?cs var:totals.category.convention ?></td>
    <td class="category total"><?cs var:totals.category.refactor ?></td>
    <td class="category total"><?cs var:totals.category.warning ?></td>
    <td class="category total"><?cs var:totals.category.error ?></td>
    <td class="total"><?cs var:totals.lines ?></td>
 </tr></tbody>
</table>
