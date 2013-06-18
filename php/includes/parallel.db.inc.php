<?php
include_once $_SERVER["DOCUMENT_ROOT"]."/includes/db.inc.php";
include_once $_SERVER["DOCUMENT_ROOT"]."/includes/dto.inc.php";
include_once $_SERVER["DOCUMENT_ROOT"]."/includes/parallel.classes.inc.php";

function getSutta($uid)
{
	
	$sql = "SELECT sutta.sutta_id,
			sutta.sutta_uid, 
			sutta.sutta_acronym,
			sutta.alt_sutta_acronym,
			sutta.sutta_text_url_link,
			sutta.sutta_name,
			sutta.volpage_info,
			sutta.alt_volpage_info
		FROM sutta
		WHERE sutta.sutta_uid = '$uid';"; 	
	
	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());

	$row = mysql_fetch_assoc($result);
	
	$sutta = new Sutta();
	
	$sutta->id = $row["sutta_id"];
	$sutta->uid = $row["sutta_uid"];
	$sutta->sutta_acronym = $row["sutta_acronym"];
	$sutta->alt_sutta_acronym = $row["alt_sutta_acronym"];
	$sutta->sutta_text_url_link = $row["sutta_text_url_link"];
	$sutta->sutta_name = $row["sutta_name"];
	$sutta->volpage_info = $row["volpage_info"];
	$sutta->alt_volpage_info = $row["alt_volpage_info"];
	
	return $sutta;
}

function getNumberOfEntries($sutta_id)
{
	 $sql = "SELECT COUNT(*) AS number_of_entries 
		        FROM correspondence
		        WHERE entry_id = $sutta_id";

		$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());      
		$row = mysql_fetch_assoc($result);
	
		return $row["number_of_entries"];
}

function getNumberOfCorrespEntries($sutta_id)
{
	 $sql = "SELECT COUNT(*) AS number_of_corresp_entries 
		        FROM correspondence
		        WHERE corresp_entry_id = $sutta_id";

		$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());      
		$row = mysql_fetch_assoc($result);
	
		return $row["number_of_corresp_entries"];
}

function getEntryByCorresp($corresp_id)
{
	$sql = "SELECT entry_id FROM correspondence
			WHERE corresp_entry_id = $corresp_id";
			
	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());      
	$row = mysql_fetch_assoc($result);

	return $row["entry_id"];
}

function getEntryID($sutta_id)
{
	// Should return 14 for 14 or 14 for 4154
	if(getNumberOfEntries($sutta_id) > 0) 
	{
		return $sutta_id;
	}
	else if(getNumberOfCorrespEntries($sutta_id) == 1)
	{
		return getEntryByCorresp($sutta_id);
	}
	
	return 0;
}

function getKeyCorrespondence($entry_id, $corresp_entry_id)
{
	$sql = "SELECT parallel.sutta_id AS parallel_id, 
				parallel.sutta_acronym AS parallel_acronym,
				parallel.volpage_info AS parallel_volpage_info,
				parallel.sutta_text_url_link AS parallel_text_url_link,
				correspondence.footnote_text,
				collection_language.collection_language_name,
				biblio_entry.biblio_entry_text
			FROM sutta AS parallel
			INNER JOIN correspondence
				ON parallel.sutta_id = correspondence.entry_id
			INNER JOIN collection_language 
					ON parallel.collection_language_id = collection_language.collection_language_id	
			LEFT JOIN biblio_entry 
					ON biblio_entry.biblio_entry_id = parallel.biblio_entry_id
			WHERE parallel.sutta_id = $entry_id AND correspondence.corresp_entry_id = $corresp_entry_id";
			
	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());
	
	$row = mysql_fetch_assoc($result);
	
	$parallel = new Parallel();
	
	$parallel->id = $row["parallel_id"];
	$parallel->acronym = $row["parallel_acronym"];
	$parallel->name = $row["parallel_name"];
	$parallel->volpage_info = $row["parallel_volpage_info"];
	$parallel->text_url_link = $row["parallel_text_url_link"];
	$parallel->footnote_text = $row["footnote_text"];
	$parallel->collection_language = $row["collection_language_name"];
	$parallel->biblio_entry_text = $row["biblio_entry_text"];
	
	return $parallel;
}

function getParallels($sutta_id)
{
	$entry_id = getEntryID($sutta_id);
		
	$sql = "SELECT parallel.sutta_id AS parallel_id, 
		parallel.sutta_acronym AS parallel_acronym,
		parallel.sutta_name AS parallel_name,
		parallel.volpage_info AS parallel_volpage_info,
		parallel.sutta_text_url_link AS parallel_text_url_link,
		correspondence.footnote_text,
		collection_language.collection_language_name,
		biblio_entry.biblio_entry_text
	FROM correspondence 
	INNER JOIN sutta AS parallel
		ON correspondence.corresp_entry_id = parallel.sutta_id	
	INNER JOIN collection_language 
		ON parallel.collection_language_id = collection_language.collection_language_id	
	LEFT JOIN biblio_entry 
		ON biblio_entry.biblio_entry_id = parallel.biblio_entry_id
	WHERE correspondence.entry_id = '$entry_id'";
		
	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());
	
	$parallels = array();
	
	while($row = mysql_fetch_assoc($result))
	{
		$next_parallel = new Parallel();
		
		$next_parallel->id = $row["parallel_id"];
		$next_parallel->acronym = $row["parallel_acronym"];
		$next_parallel->name = $row["parallel_name"];
		$next_parallel->volpage_info = $row["parallel_volpage_info"];
		$next_parallel->text_url_link = $row["parallel_text_url_link"];
		$next_parallel->footnote_text = $row["footnote_text"];
		$next_parallel->collection_language = $row["collection_language_name"];
		$next_parallel->biblio_entry_text = $row["biblio_entry_text"];
		
		$parallels[] = $next_parallel;
	}
	
	// The sutta is matched in the corresp_entry_id row. We now have to
	// add the sutta that matches the entry_id in that same row.
	if($entry_id != $sutta_id)
	{
		$parallels[] = getKeyCorrespondence($entry_id, $sutta_id);
	}
	
	return $parallels;
}

function newGetParallels($sutta_id)
{
	$factory = new ParallelFactory();
	$collection = $factory->makeCollection($sutta_id);
	$details = new ParallelDetails($collection);
	return $details->getListOfParallels();
}
?>
