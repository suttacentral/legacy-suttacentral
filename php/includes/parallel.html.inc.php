<?php 
	include_once $_SERVER["DOCUMENT_ROOT"]."/includes/parallel.db.inc.php";
	include_once $_SERVER["DOCUMENT_ROOT"]."/includes/division.db.inc.php";

	$sutta = getSutta($uid); 

	// Note, the parallels engine uses the sutta_id, not the sutta_uid.
	$parallels = newGetParallels($sutta->id);

	// This flag will be set to true if any of the suttas 
	// has the alt_sutta_acronym displayed.
	$has_alt_sutta_acronym = false; 
	// This flag will be set to true if any of the suttas 
	// has the alt_volpage_info displayed.
	$has_alt_volpage_info = false; 
?>
<div id="onecol">
<table>
<caption>
<?php

echo "Details for <strong><a href=\"";
echo $sutta->sutta_text_url_link . "\">";
echo $sutta->sutta_acronym . "</a> ";


echo $sutta->sutta_name;
echo "</strong>";

?>
</caption>
<thead>
<tr>
<th>Language</th>
<th>Identifier</th>
<th>Title</th>
<th>Vol/Page</th>
<th>Translations</th>
</tr>
</thead>
<tbody>
<?php foreach($parallels as $parallel): ?>
<?php 
if($parallel->is_origin)
{
	echo "<tr class=\"origin\">"; 
}
else
{
	echo "<tr>";
}
?>
<td><?php echo $parallel->collection_language; ?></td>
<td>
<?php 
if($parallel->text_url_link != "")
{
	echo "<a href=\"" . $parallel->text_url_link . "\"";
	echo "title=\"Go to original text for " . $parallel->acronym . ".\">";
	echo $parallel->acronym . "</a>";
}
else
{
	echo $parallel->acronym;
}

if ($parallel->alt_acronym && $parallel->alt_acronym != $parallel->acronym)
{
    echo ' <span class="altAcronym">' . str_replace(" ", "&nbsp;", $parallel->alt_acronym) . '</span>';
    $has_alt_sutta_acronym = true;
}

if($parallel->is_partial) echo "*";
?>
</td>
<td><?php echo $parallel->name; ?>
</td>
<td>
<?php 
echo $parallel->volpage_info; 

if ($parallel->alt_volpage_info && $parallel->volpage_info != $parallel->alt_volpage_info)
{
    echo ' <span class="altVolPage">' . str_replace(" ", "&nbsp;", $parallel->alt_volpage_info) . '</span>';
    $has_alt_volpage_info = true;
}
   
if($parallel->footnote_text != "")
{
	echo "<a class=\"note\"><div class=\"tri\">&nbsp;▶</div><span class=\"deets\">";
	echo $parallel->footnote_text; 
	echo "</span></a>";
}
if($parallel->biblio_entry_text != "")
{
	echo "<a class=\"bib\"><div class=\"tri\">&nbsp;▶</div><span class=\"deets\">";
	echo $parallel->biblio_entry_text;
	echo "</span></a>";
}
?>
</td>
<td>
<?php $sutta = $parallel // HACK translations script expects $sutta, not $parallel ?>
<?php include $_SERVER["DOCUMENT_ROOT"]."/includes/translation.list.html.inc.php"; ?>
</td>
</tr>
<?php endforeach; ?>
</tbody>
<tfoot>
<?php if($has_alt_sutta_acronym): ?>
<tr><td colspan="4">[...] indicates alternative <span class="smallcaps">PTS</span> or Taishō  numbering.</td><tr>
<?php endif; ?>
<?php if($has_alt_volpage_info): ?>
<tr><td colspan="4"><...> refers to <span class="smallcaps">PTS</span> 1998 (Somaratne) edition of SN Vol I.</td></tr>
<?php endif; ?>
</tfoot>
</table>
</div>