<?php
	include_once $_SERVER["DOCUMENT_ROOT"]."/includes/division.db.inc.php";
	$caption_data = getDivisionCaptionData($uid);
	$has_vaggas = divisionHasVaggas($uid);	
	
	// This flag will be set to true if any of the suttas 
	// has the alt_sutta_acronym displayed.
	$has_alt_sutta_acronym = false; 
	// This flag will be set to true if any of the suttas 
	// has the alt_volpage_info displayed.
	$has_alt_volpage_info = false; 
?>
<div id="onecol">
<table>
<caption>Collection: <strong><?php echo $caption_data->collection_name ?></strong> — Division: <strong>
<?php echo $caption_data->division_name . " (" . $caption_data->division_acronym . ")" ?> </strong>
</caption>
<thead>
<tr>
<th>Identifier</th>
<th>Title</th>
<th>Vol/Page</th>
<th>Parallels</th>
<th class="transcol">Translations</th>
</tr>
</thead>
<tbody>
<?php 
if($has_vaggas) // Include vaggas in division view
{
	$subdivisions = getSubdivisionsWithVaggas($uid);
	foreach($subdivisions as $subdivision)
	{
		// If the subdivision has a name, display it. 
		// Perhaps dash should be changed to null in the database.
		if($subdivision->name != "−" && $subdivision->name != "")
		{
			echo "<tr><td colspan=\"5\" class=\"subdivision\">" . $subdivision->name . "</td></tr>";
		}
		
		// Display vagga titles
		foreach($subdivision->vaggas as $vagga)
		{
			echo "<tr><td colspan=\"5\" class=\"vagga\">" . $vagga->name . "</td></tr>";
			$suttas = $vagga->suttas;
			// Display sutta rows.
			include $_SERVER["DOCUMENT_ROOT"]."/includes/sutta.list.html.inc.php";
		}
	}
}
else // Some divisions don't have vaggas. Display suttas without vagga or subdivision titles.
{
	$suttas = getSuttasInDivision($uid);
	include $_SERVER["DOCUMENT_ROOT"]."/includes/sutta.list.html.inc.php";
}
?>
</tbody>
<tfoot>
<?php if($has_alt_sutta_acronym): ?>
<tr><td colspan="4">[...] indicates alternative PTS or Taisho numbering.</td><tr>
<?php endif; ?>
<?php if($has_alt_volpage_info): ?>
<tr><td colspan="4"><...> refers to PTS 1998 (Somaratne) edition of SN Vol I.</td></tr>
<?php endif; ?>
</tfoot>
</table>
</div>
