<header>
<div class="headerBg">
<a href="/">
<p class="wheel">☸</p>
<hgroup>
<h1>SuttaCentral</h1><br>
<h2>Early Buddhist texts, translations, and parallels</h2>
</hgroup>
</a>

<?php include $_SERVER["DOCUMENT_ROOT"]."/includes/search.form.html.inc.php"; ?>
<?php include_once $_SERVER["DOCUMENT_ROOT"]."/includes/url.helper.php"; ?>

<div id="navbar">
<?php for($collection_num = 0; $collection_num < count($collections); $collection_num++) 
{
if($collection_num == 0)
{ 
	$collection_class = "topnavright";
}
else if($collection_num == count($collections) - 1) 
{
	$collection_class = "topnavleft";
}
else
{
	$collection_class = "topnav";
}

$collection = $collections[$collection_num];
?>
<nav><span class="<?php echo $collection_class; ?>"><?php echo $collection->name ?></span>
<ul>
	<?php foreach($collection->divisions as $division): ?>
	<li><a href="<?php echo getDivisionURL($division->uid); ?>"><?php echo $division->name ?></a></li>
	<?php endforeach; ?>
</ul>
</nav>
<?php
} 
?>
</div>
</div>
</header>
