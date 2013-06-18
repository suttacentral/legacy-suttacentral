<?php
function acronymToId($acronym)
{
	return strtolower(str_replace(" ", " ", $acronym)); 
}

function getDivisionURL($uid)
{
	return "/" . $uid;
}

// For the abbreviated division caption.
function getFullDivisionURL($uid)
{
	return "/" . $uid . "/full";
}

function getParallelURL($uid)
{
	return "/" . $uid;
}
?>
