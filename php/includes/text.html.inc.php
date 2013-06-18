<?php
include_once $_SERVER["DOCUMENT_ROOT"]."/includes/db.inc.php";
$file_name = $_SERVER["DOCUMENT_ROOT"] . "/text/" . $text_lang . "/" . $text_acronym . ".html";
if(file_exists($file_name) == false) 
{ 
	preg_match('@/([^/]+)\.html@', $file_name, $matches);
 
	$uid = $matches[1];
 
	$sql = "SELECT sutta_text_url_link 
			FROM sutta 
			WHERE sutta.sutta_uid = '$uid'";

	$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());
	$row = mysql_fetch_assoc($result) or die ("No such sutta: " . $uid);

	$url = $row["sutta_text_url_link"];
	
	preg_match('@/([^/]+)/pi/@', $url, $matches);

	$text_acronym = $matches[1];

	$file_name = $_SERVER["DOCUMENT_ROOT"] . "/text/" . $text_lang . "/" . $text_acronym . ".html";
}
$file_contents = file_get_contents($file_name);
$start_tag_pos = strpos($file_contents, "<body>") + strlen("<body>");
$end_tag_pos = strpos($file_contents, "</body>");

echo substr($file_contents, $start_tag_pos, $end_tag_pos - $start_tag_pos);
?>
