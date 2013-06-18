<?php include_once $_SERVER["DOCUMENT_ROOT"]."/includes/url.helper.php"; ?>
<section>
<h1>Sutta-piṭaka</h1>
	<?php foreach($collections as $collection): ?>
	<ul>
		<li><h2><?php echo $collection->name; ?></h2></li>
		<?php foreach($collection->divisions as $division): ?>
		<li><a href="<?php echo getDivisionURL($division->uid); ?>"><?php echo $division->name; ?></a></li>
		<?php endforeach; ?>
	</ul>
	<?php endforeach; ?>
</ul>
</section>
