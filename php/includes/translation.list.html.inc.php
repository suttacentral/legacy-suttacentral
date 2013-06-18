<?php
	include_once $_SERVER["DOCUMENT_ROOT"]."/includes/division.db.inc.php"; // Refactor - getReferences is used by division and parallel view.

	$references = getReferences($sutta->id);
	
	$num_references = count($references);
	for($ref_index = 0; $ref_index < $num_references; $ref_index++)
	{ 
		$reference = $references[$ref_index];
		echo "<a href=\"" . $reference->url . "\" class=\"tran\" title=\"" . $reference->text . "\">" . $reference->language . "</a>";
		if($ref_index < $num_references - 1) // Insert pipe between language abbreviations
		{
			echo " | ";
		}
	}
?>
