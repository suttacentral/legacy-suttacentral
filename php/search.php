<?php
    $q = $_GET["ya"];
    $from = $_GET["from"];
    $range = $_GET["range"];
    if (!$q) {$q = "winkitybobbob";}
    $ajax = $_GET["ajax"];
    if ($ajax) {
        if (!$from) $from = 0;
        if (!$range) $range = 10;
        include $_SERVER["DOCUMENT_ROOT"]."/includes/search.results.html.inc.php";
        exit(0);
    }
    if (!$from) $from = 0;
    if (!$range) $range = 25;
?>
<!DOCTYPE html>
<html lang="en">
<?php include $_SERVER["DOCUMENT_ROOT"]."/includes/head.html.inc.php"; ?>
<body>

<?php
// This is the  controller for searching.


    {
        include $_SERVER["DOCUMENT_ROOT"]."/includes/collections.db.inc.php";
        $collections = array_reverse(getHeaderData());
        echo "<div id=\"wrap\">";
        
        include $_SERVER["DOCUMENT_ROOT"]."/includes/static.menu.header.html.inc.php";

?><script>
	(function() {
		var cx = '004290292043968432595:y22hs7b-duk';
		var gcse = document.createElement('script');
		gcse.type = 'text/javascript';
		gcse.async = true;
		gcse.src = (document.location.protocol == 'https:' ? 'https:' : 'http:') +
			'//www.google.com/cse/cse.js?cx=' + cx;
		var s = document.getElementsByTagName('script')[0];
		s.parentNode.insertBefore(gcse, s);
	})();
</script>
<div id="google-site-search"><h1>Full Text Search</h1><gcse:search></gcse:search></div>
<div id="onecol">
<?php
        

        include $_SERVER["DOCUMENT_ROOT"]."/includes/search.results.html.inc.php";
        
        echo "</div></div>";
        include $_SERVER["DOCUMENT_ROOT"]."/includes/footer.html.inc.php";
}
?>
</body>
</html>