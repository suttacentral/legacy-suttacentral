<?php
include_once $_SERVER["DOCUMENT_ROOT"]."/includes/db.inc.php";
include_once $_SERVER["DOCUMENT_ROOT"]."/includes/dto.inc.php";

function getDivisionCaptionData($uid)
{
	$sql = "SELECT collection.collection_id, 
				collection.collection_name, 
				division.division_id, 
				division.division_uid, 
				division.division_name, 
				division.division_acronym
		FROM collection INNER JOIN division 
		ON collection.collection_id = division.collection_id
		WHERE division.division_uid = '$uid' ORDER BY collection.collection_id, division.division_id"; 	

	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());
	$row = mysql_fetch_assoc($result);
	
	$caption_data = new DivisionCaptionData();
	$caption_data->collection_name = $row["collection_name"];
	$caption_data->division_name = $row["division_name"];
	$caption_data->division_uid =  $row["division_uid"];
	$caption_data->division_acronym = $row["division_acronym"];
	
	return $caption_data;
}

function getSubDivisionCaptionData($uid)
{
	$sql = "SELECT collection.collection_id, 
			collection.collection_name, 
			division.division_id, 
			division.division_name, 
			division.division_acronym,
			subdivision.subdivision_name
		FROM collection 
		INNER JOIN division 
			ON collection.collection_id = division.collection_id
		INNER JOIN subdivision 
			ON division.division_id = subdivision.division_id
		WHERE subdivision.subdivision_uid = '$uid'";
		
	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());
	$row = mysql_fetch_assoc($result);
	
	$caption_data = new SubdivisionCaptionData();
	$caption_data->collection_name = $row["collection_name"];
	$caption_data->division_name = $row["division_name"];
	$caption_data->division_acronym = $row["division_acronym"];
	$caption_data->subdivision_name = $row["subdivision_name"];
	
	return $caption_data;
}

function getSubdivision($uid)
{
	$sql = "SELECT subdivision_id,
				subdivision_uid,
				subdivision_name, 
				subdivision_acronym 
			FROM subdivision
			INNER JOIN division 
				ON subdivision.division_id = division.division_id
			WHERE subdivision_uid = '$uid'";
	
	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());
	$row = mysql_fetch_assoc($result);
	
	$subdivision = new Subdivision();
	$subdivision->id = $row['subdivision_id'];
	$subdivision->uid = $row['subdivision_uid'];
	$subdivision->name = $row['subdivision_name'];
	$subdivision->acronym = $row['subdivision_acronym'];
	
	return $subdivision;
}



function getSuttasInVagga($vagga_id)
{
	$sql = "SELECT sutta.sutta_id,
			sutta.sutta_uid,
			sutta.sutta_acronym,
			sutta.alt_sutta_acronym,
			sutta.sutta_name,
			sutta.volpage_info,
			sutta.alt_volpage_info,
			sutta_text_url_link
		FROM sutta
		WHERE sutta.vagga_id = $vagga_id
		ORDER BY sutta.sutta_number";

	$result = mysql_query($sql);

	$suttas = array();
	
	while($row = mysql_fetch_assoc($result))
	{
		$sutta = new Sutta();
		
		$sutta->id = $row["sutta_id"];
		$sutta->uid = $row["sutta_uid"];
		$sutta->sutta_acronym = $row["sutta_acronym"];
		$sutta->alt_sutta_acronym = $row["alt_sutta_acronym"];
		$sutta->name = $row["sutta_name"];
		$sutta->volpage_info = $row["volpage_info"];
		$sutta->alt_volpage_info = $row["alt_volpage_info"];
		$sutta->sutta_text_url_link = $row["sutta_text_url_link"];
		
		$suttas[] = $sutta;
	}
	return $suttas;
	
}

function getVaggas($uid)
{

/*	$sql = "SELECT vagga.vagga_id,
				vagga.vagga_name
			FROM vagga
			INNER JOIN subdivision ON vagga.subdivision_id = subdivision.subdivision_id
			WHERE subdivision.subdivision_uid = '$uid'";*/

        //Hack by Nandiya to make it work (Vagga subdivision_id column is corrupt. But suttas 'know' what vagga they are in so the below query gets a list of distinct vaggas and uses those as the basis for a query on the vagga table. Since I don't know what I'm doing I used a sub-query, although it must be said, breaking the problem up in that way makes it more understandable.
        $sql = "SELECT vagga.vagga_id,
                                vagga.vagga_name
                        FROM vagga
                        WHERE vagga.vagga_id IN (SELECT DISTINCT vagga_id
                            FROM  `sutta`
                            INNER JOIN subdivision ON sutta.subdivision_id = subdivision.subdivision_id
                            WHERE subdivision.subdivision_uid = '$uid')";

	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());
	
	$vaggas = array();
	
	while($row = mysql_fetch_assoc($result))
	{
		$vagga = new Vagga();
		
		$vagga->id = $row["vagga_id"];
		$vagga->name = $row["vagga_name"];
		
		$vagga->suttas = getSuttasInVagga($vagga->id);		
		
		$vaggas[] = $vagga;
	}
	
	return $vaggas;
}

// For the long division view.
function getSubdivisionsAlone($uid)
{
	$sql = "SELECT subdivision.subdivision_id,
				subdivision.subdivision_uid,
				subdivision.subdivision_name,
				subdivision.subdivision_acronym
			FROM division	
			INNER JOIN subdivision ON subdivision.division_id = division.division_id
			WHERE division.division_uid = '$uid'";
			
	$result = mysql_query($sql);

	$subdivisions = array();
	
	while($row = mysql_fetch_assoc($result))
	{
		$subdivision = new Subdivision();
		
		$subdivision->id = $row["subdivision_id"];
		$subdivision->uid = $row["subdivision_uid"];
		$subdivision->name = $row["subdivision_name"];
		$subdivision->acronym = $row["subdivision_acronym"];
		
		$subdivisions[] = $subdivision;
	}
	
	return $subdivisions;
}

function getSubdivisionUrl($subdivision)
{
	return "/" . $subdivision->uid;
}

function getSubdivisionsWithVaggas($uid)
{
	$sql = "SELECT subdivision.subdivision_id,
			subdivision.subdivision_uid,
			subdivision.subdivision_name
		FROM division	
		INNER JOIN subdivision ON subdivision.division_id = division.division_id
		WHERE division.division_uid = '$uid'";

	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());

	$subdivisions = array();
	
	while($row = mysql_fetch_assoc($result))
	{
		$subdivision = new Subdivision();
		
		$subdivision->id = $row["subdivision_id"];
		$subdivision->uid = $row["subdivision_uid"];
		$subdivision->name = $row["subdivision_name"];
		
		$subdivision->vaggas = getVaggas($subdivision->uid);
		$subdivisions[] = $subdivision;
	}

	return $subdivisions;
}

function getReferences($sutta_id)
{
	$sql = "SELECT reference.reference_language_id, 
				reference.reference_seq_nbr,
				reference.abstract_text, 
				reference.reference_url_link, 
				reference_language.iso_code_2
			FROM reference
			INNER JOIN reference_language 
				ON reference.reference_language_id = reference_language.reference_language_id
			WHERE sutta_id = $sutta_id
			ORDER BY reference_language_id, reference_seq_nbr;";
			
	$result = mysql_query($sql);
	
	$references = array();

	while($row = mysql_fetch_assoc($result))
	{
		$language_id   = $row["reference_language_id"];
		$abstract_text = $row["abstract_text"];
		$reference_url_link = $row["reference_url_link"];
		$iso_code_2 = $row["iso_code_2"];
		
		$next_reference = new Reference();
		$references[] = $next_reference;
		
		$next_reference->language = $iso_code_2;
		$next_reference->text = $abstract_text;
		$next_reference->url = $reference_url_link;
	}
	
	return $references;
}

function getSuttasInSubdivision($uid)
{
	$sql = "SELECT sutta.sutta_id,
	   sutta.sutta_uid,
	   sutta.sutta_acronym,
	   sutta.alt_sutta_acronym,
	   sutta.sutta_name,
	   sutta.volpage_info,
	   sutta.alt_volpage_info,
	   sutta_text_url_link
	FROM subdivision
	INNER JOIN sutta ON sutta.subdivision_id = subdivision.subdivision_id
	WHERE subdivision.subdivision_uid = '$uid'
	ORDER BY sutta.sutta_number";
	
	$result = mysql_query($sql);

	$suttas = array();
	
	while($row = mysql_fetch_assoc($result))
	{
		$sutta_id = $row["sutta_id"];
		$sutta_uid = $row["sutta_uid"];
		$sutta_name = $row["sutta_name"];
		$sutta_acronym = $row["sutta_acronym"];
		$alt_sutta_acronym = $row["alt_sutta_acronym"];
		$volpage_info = $row["volpage_info"];
		$alt_volpage_info = $row["alt_volpage_info"];
		$sutta_text_url_link = $row["sutta_text_url_link"];
		
		$next_sutta = new Sutta();
		
		$suttas[] = $next_sutta;
		$next_sutta->id = $sutta_id;
		$next_sutta->uid = $sutta_uid;
		$next_sutta->name = $sutta_name;
		$next_sutta->sutta_acronym = $sutta_acronym;
		$next_sutta->alt_sutta_acronym = $alt_sutta_acronym;
		$next_sutta->volpage_info = $volpage_info;
		$next_sutta->alt_volpage_info = $alt_volpage_info;
		$next_sutta->sutta_text_url_link = $sutta_text_url_link;
	}
	
	return $suttas;
}

function getSuttasInDivision($uid)
{
	$sql = "SELECT sutta.sutta_id,
		sutta.sutta_uid, 	
		sutta.sutta_acronym,
		sutta.alt_sutta_acronym,
		sutta.sutta_name,
		sutta.volpage_info,
		sutta.alt_volpage_info,
   		sutta_text_url_link
	FROM division 
	INNER JOIN subdivision ON subdivision.division_id = division.division_id
	INNER JOIN sutta ON sutta.subdivision_id = subdivision.subdivision_id
	WHERE division.division_uid = '$uid'
	ORDER BY sutta.sutta_number";
	
	$result = mysql_query($sql) or die ('Query failed in : getSuttasInDivision()' . mysql_error());

	$suttas = array();
	
	while($row = mysql_fetch_assoc($result))
	{
		$sutta_id = $row["sutta_id"];
		$sutta_uid = $row["sutta_uid"];
		$sutta_name = $row["sutta_name"];
		$sutta_acronym = $row["sutta_acronym"];
		$alt_sutta_acronym = $row["alt_sutta_acronym"];
		$volpage_info = $row["volpage_info"];
		$alt_volpage_info = $row["alt_volpage_info"];
		$sutta_text_url_link = $row["sutta_text_url_link"];
		
		$next_sutta = new Sutta();
		
		$suttas[] = $next_sutta;
		$next_sutta->id = $sutta_id;
		$next_sutta->uid = $sutta_uid;
		$next_sutta->name = $sutta_name;
		$next_sutta->sutta_acronym = $sutta_acronym;
		$next_sutta->alt_sutta_acronym = $alt_sutta_acronym;
		$next_sutta->volpage_info = $volpage_info;
		$next_sutta->alt_volpage_info = $alt_volpage_info;
		$next_sutta->sutta_text_url_link = $sutta_text_url_link;
	}
	
	return $suttas;
}

function subDivisionHasVaggas($uid)
{
	$sql = "SELECT COUNT(*) AS vaggas_in_subdivision
			FROM subdivision
			INNER JOIN vagga ON vagga.subdivision_id = subdivision.subdivision_id
			WHERE subdivision.subdivision_uid = '$uid'";
		
	$result = mysql_query($sql);
	
	if($result)
	{
		$row = mysql_fetch_assoc($result);
		$number_of_vaggas = $row["vaggas_in_subdivision"];
		if($number_of_vaggas > 0) return true;
	}
		
	return false;
}

function divisionHasVaggas($uid)
{
	// HACK: Actually there is a single 
	// vagga with nothing in it.
	if($uid == "da") return false;
	
	$sql = "SELECT COUNT(*) AS vaggas_in_division
			FROM division 
			INNER JOIN subdivision ON subdivision.division_id = division.division_id
			INNER JOIN vagga ON vagga.subdivision_id = subdivision.subdivision_id
			WHERE division.division_uid = '$uid'";
		
	$result = mysql_query($sql);
	
	if($result)
	{
		$row = mysql_fetch_assoc($result);
		$number_of_vaggas = $row["vaggas_in_division"];
		if($number_of_vaggas > 0) return true;
	}
		
	return false;
}

?>
