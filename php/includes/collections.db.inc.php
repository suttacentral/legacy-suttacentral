<?php

include_once $_SERVER["DOCUMENT_ROOT"]."/includes/db.inc.php";
include_once $_SERVER["DOCUMENT_ROOT"]."/includes/dto.inc.php";


function getHeaderData()
{	
	// The query to perform to obtain the data needed for the page headers.
	$sql = "SELECT collection.collection_id, 
				collection.collection_name, 
				division.division_id, 
				division.division_uid, 
				division.division_name, 
				division_acronym
			FROM collection INNER JOIN division 
			ON collection.collection_id = division.collection_id
			ORDER BY collection.collection_id, division.division_id"; 	
	
	
	$result = mysql_query($sql);

	$collections = array();
	while($row = mysql_fetch_assoc($result))
	{
		$collection_id = $row["collection_id"];
		$collection_name = $row["collection_name"];
		$division_id = $row["division_id"];
		$division_uid = $row["division_uid"];
		$division_name = $row["division_name"];
		$division_acronym = $row["division_acronym"];
		
		// Create the first collection
		if(count($collections) == 0)
		{
			$next_collection = new Collection();
			
			$collections[] = $next_collection;
			
			$next_collection->id = $collection_id;
			$next_collection->name = $collection_name;
			$next_collection->divisions = array();
		}

		$num_collections = count($collections);

		if($collections[$num_collections - 1]->id != $collection_id)
		{
			$next_collection = new Collection();
			$collections[] = $next_collection;
			
			$next_collection->id = $collection_id;
			$next_collection->name = $collection_name;
			$next_collection->divisions = array();
		}
		
		$num_divisions = count($next_collection->divisions);
		
		$next_division = new Division();
		
		$next_collection->divisions[$num_divisions + 1] = $next_division;
		$next_division->id = $division_id;
		$next_division->uid = $division_uid;
		$next_division->name = $division_name;
		$next_division->acronym = $division_acronym;
	}
	
	return $collections;
}

function maxDivisions($collections)
{
	// Calculate the largest number of divisions.
	$max_number_of_divisions = 0;
	foreach($collections as $collection)
	{
		$number_of_divisions = count($collection->divisions);
		if( $number_of_divisions > $max_number_of_divisions)
		{
			$max_number_of_divisions = $number_of_divisions;
		}
	}
	return $max_number_of_divisions;	
}
?>
