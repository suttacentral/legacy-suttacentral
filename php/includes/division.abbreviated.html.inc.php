<?php
	include_once $_SERVER["DOCUMENT_ROOT"]."/includes/division.db.inc.php";
	include_once $_SERVER["DOCUMENT_ROOT"]."/includes/url.helper.php";
	$caption_data = getDivisionCaptionData($uid);
	$has_vaggas = divisionHasVaggas($uid);	
?>
<div id="onecol">
<table>
<caption>Collection: <strong><?php echo $caption_data->collection_name ?></strong> — Division: 
<strong>
<a href="<?php echo getFullDivisionURL($caption_data->division_uid) ?>">
<?php echo $caption_data->division_name ?>
</a>
<?php echo " (" . $caption_data->division_acronym . ")" ?>
</strong>

</caption>
<thead>
<tr>
<th>Identifier</th>
<th>Subdivision</th>
</tr>
</thead>
<tbody>
<?php 
$subdivisions = getSubdivisionsAlone($uid);

foreach($subdivisions as $subdivision)
{
	// If the subdivision has a name, display it. 
	// Perhaps dash should be changed to null in the database.
	if($subdivision->name != "-" && $subdivision->name != "")
	{
		echo "<tr><td>" . $caption_data->division_acronym . " " . $subdivision->acronym . "</td><td><a href='" .  getSubdivisionUrl($subdivision)	. "'>" .  $subdivision->name . "</a></td></tr>\n";
	}
}
?>
</tbody>
</table>
</div>
