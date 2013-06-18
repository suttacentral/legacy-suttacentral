<!DOCTYPE html>
<html lang="en">
<?php include $_SERVER["DOCUMENT_ROOT"]."/includes/head.html.inc.php"; ?>
<body>

<?php
if(isset($_GET["show"]))
{
	$view_to_show = $_GET["show"];
}
else
{
	$view_to_show = "home";
}

// Show home page view
if($view_to_show == "home")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	echo "<div id=\"wrap\">";
	$collections = getHeaderData();
	include $_SERVER["DOCUMENT_ROOT"]."/includes/home.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($view_to_show == "about")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/about.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($view_to_show == "contacts")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/contacts.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($view_to_show == "methodology")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/methodology.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($view_to_show == "bibliography")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/bibliography.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($view_to_show == "sutta_numbering")
{
        include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
        $collections = array_reverse(getHeaderData());
        echo "<div id=\"wrap\">";
        include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
        include $_SERVER["DOCUMENT_ROOT"]."/includes/sutta_numbering.html.inc.php";
        echo "</div>";
        include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($view_to_show == "abbreviations")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/abbreviations.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($view_to_show == "help")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/help.html.inc.php";
	echo "</div>";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
else if($view_to_show == "downloads")
{
	include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
	$collections = array_reverse(getHeaderData());
	echo "<div id=\"wrap\">";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";
	include $_SERVER["DOCUMENT_ROOT"]."/includes/downloads.html.inc.php";
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
</body></html>
