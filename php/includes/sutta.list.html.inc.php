<?php include_once $_SERVER["DOCUMENT_ROOT"]."/includes/parallel.db.inc.php"; ?>
<?php include_once $_SERVER["DOCUMENT_ROOT"]."/includes/url.helper.php"; ?>

<?php foreach($suttas as $sutta): ?>
<tr>
<td>
<?php
	// Quite a lot of code repatition dealing with identifiers. 
	// We should try and refactor this code so the linkification
	// and unspaceification is done in one place.
	if($sutta->sutta_text_url_link != "") // If we have a link display it
	{
		echo "<a href=\"" . $sutta->sutta_text_url_link . 
			 "\" title=\"Go to original text for " . 
			 str_replace(" ", "&nbsp;", $sutta->sutta_acronym) . ".\">" . 
			 str_replace(" ", "&nbsp;", $sutta->sutta_acronym) . "</a>";
	} 
	else
	{
		echo str_replace(" ", "&nbsp;", $sutta->sutta_acronym); // Otherwise show the unlinked acronym.
	}
	if ($sutta->alt_sutta_acronym && $sutta->alt_sutta_acronym != $sutta->sutta_acronym)
	{
        echo ' <span class="altAcronym">' . str_replace(" ", "&nbsp;", $sutta->alt_sutta_acronym) . '</span>';
		$has_alt_sutta_acronym = true;
    }
?>
</td>
<td><?php echo $sutta->name; ?></td>
<td><?php echo $sutta->volpage_info;
if ($sutta->alt_volpage_info && $sutta->volpage_info != $sutta->alt_volpage_info)
{
    echo ' <span class="altVolPage">' . str_replace(" ", "&nbsp;", $sutta->alt_volpage_info) . '</span>';
    $has_alt_volpage_info = true;
}
?></td>
<td>
<?php // Some nasty stuff to get a list of parallels.
$parallels = newGetParallels($sutta->id);
$num_parallels = count($parallels);
for($parallel_index = 0; $parallel_index < $num_parallels; $parallel_index++)
{
	$parallel = $parallels[$parallel_index];
	if($parallel->is_origin == false)
	{
	if($parallel->text_url_link != "") // If we have a link display it
	{
		echo "<a href=\"" . $parallel->text_url_link . 
			 "\" title=\"Go to original text for " . 
			 str_replace(" ", "&nbsp;", $parallel->acronym) . ".\">" . 
			 str_replace(" ", "&nbsp;", $parallel->acronym) . "</a>";
	} 
	else
	{
		echo str_replace(" ", "&nbsp;", $parallel->acronym); // Otherwise show the unlinked acronym.
	}
	
	// Display parallels with asterisk.
	if($parallel->is_partial) echo "*";
	
	if($parallel_index != $num_parallels - 1) // If last parallel, don't insert a comma
	{
		echo ", ";
	}
	else
	{
		echo " "; // Instead insert a space before the details link
		}
	}
}
?>
<?php if($num_parallels > 0): ?>
<a href="<?php echo getParallelURL($sutta->uid) ?>" title="Correspondence details for <?php echo str_replace(" ", "&nbsp;", $sutta->sutta_acronym) ?>." class="details">▶</a>
<?php endif; ?>
</td>
<td class="transcol">
<?php include $_SERVER["DOCUMENT_ROOT"]."/includes/translation.list.html.inc.php"; ?>
</td>
</tr>
<?php endforeach; ?>
