<!DOCTYPE html>
<html lang="en">
<?php include $_SERVER["DOCUMENT_ROOT"]."/includes/head.html.inc.php"; ?>
<body>

<?php
// This is the  controller for the browsing actions.
$browsing_view = $_GET["show"];

// This ID is qnique for all sutta, subdivisions and divisions.
$uid = $_GET["uid"];

if($browsing_view == "fulldivision")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/division.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($browsing_view == "division")
{
	$longdivisions = array("sn", "an", "kn", "ea", "t", "sht", "sa", "oa");
	
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	if(in_array($uid, $longdivisions))
	{
		include $_SERVER["DOCUMENT_ROOT"]."/includes/division.abbreviated.html.inc.php";
	}
	else
	{
		include $_SERVER["DOCUMENT_ROOT"]."/includes/division.html.inc.php";
	}
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($browsing_view == "subdivision")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/subdivision.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($browsing_view == "parallel")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/parallel.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($browsing_view == "text")
{
	$text_acronym = $_GET["text_acronym"];
	$text_lang = $_GET["text_lang"];
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/text.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
?>
<script type='text/javascript'>

var _ues = {
host:'suttacentral.userecho.com',
forum:'18340',
lang:'en',
tab_icon_show:false,
tab_corner_radius:5,
tab_font_size:20,
tab_image_hash:'ZmVlZGJhY2s%3D',
tab_chat_hash:'Y2hhdA%3D%3D',
tab_alignment:'right',
tab_text_color:'#FFFFFF',
tab_text_shadow_color:'#A8A8A855',
tab_bg_color:'#A4D1BE',
tab_hover_color:'#F45C5C'
};

(function() {
    var _ue = document.createElement('script'); _ue.type = 'text/javascript'; _ue.async = true;
    _ue.src = ('https:' == document.location.protocol ? 'https://' : 'http://') + 'cdn.userecho.com/js/widget-1.4.gz.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(_ue, s);
  })();

</script>
</body>
</html>
