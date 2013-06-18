<?php

include_once $_SERVER["DOCUMENT_ROOT"]."/includes/db.inc.php";

class Division
{
	public $id;
	public $name;
	public $acronym;
	
	public function __construct($id, $name, $acronym)
	{
		$this->id = $id;
		$this->name = $name;
		$this->acronym = $acronym;
	}
}

class Collection
{
	public $id;
	public $name;
	public $divisions;
  
	public function __construct($id, $name)
	{
		$this->id = $id;
		$this->name = $name;
		$this->divisions = array();
	}
}

class CollectionLanguage
{
	public $id;
	public $language;
	public $collections;
	
	public function __construct($id, $language)
	{
		$this->id = $id;
		$this->language = $language;
		$this->collections = array();
	}
}

class MenuFactory
{
	private function getDivisions($collection_id)
	{
		$sql = "SELECT * 
				FROM division
				WHERE collection_id = $collection_id";
				
		$result = mysql_query($sql);
		
		$divisions = array();
		
		while($row = mysql_fetch_assoc($result))
		{
			$id = $row["division_id"];
			$name = $row["division_name"];
			$acronym = $row["division_acronym"];
			
			$divisions[] = new Division($id, $name, $acronym);
		}
		
		return $divisions;
	}
	
	private function getCollections($language_id)
	{
		$sql = "SELECT * 
				FROM collection
				WHERE collection_language_id = $language_id";
				
		$result = mysql_query($sql);
		
		$collections = array();
		
		while($row = mysql_fetch_assoc($result))
		{
			$id = $row["collection_id"];
			$name = $row["collection_name"];
			
			$collections[] = new Collection($id, $name);
		}
	
		foreach($collections as $collection)
		{
			$collection->divisions = $this->getDivisions($collection->id);
		}
		
		return $collections;
	}
	
	public function getCollectionLanguages()
	{
		$sql = "SELECT * 
				FROM collection_language";
				
		$result = mysql_query($sql);
		
		$languages = array();
		
		while($row = mysql_fetch_assoc($result))
		{			
			$id 	  = $row["collection_language_id"];
			$lang = $row["collection_language_name"];
			$languages[] = new CollectionLanguage($id, $lang);
		}
		
		foreach($languages as $language)
		{		
			$language->collections = $this->getCollections($language->id);
		}
		
		return $languages;
	}
}

?>
