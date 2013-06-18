<?php

class Division
{
	public $id;
	public $uid;
	public $name;
	public $acronym;
	public $subdivisions;
}

class Subdivision
{
	public $id;
	public $uid;
	public $acronym;
	public $suttas;
}

class Collection
{
  public $id;
  public $name;
  public $divisions;
}

class DivisionCaptionData
{
	public $collection_name;
	public $division_uid; // For linkafying the caption to the long view.
	public $division_name;
	public $division_acronym;
}

class SubdivisionCaptionData
{
	public $collection_name;
	public $division_name;
	public $division_acronym;
	public $subdivision_name;
}
class Vagga
{
	public $id;
	public $vagga_name;
	public $suttas;
}

class Sutta
{
	public $id;
	public $uid;
	public $name;
	public $volpage_info;
	public $alt_volpage_info;
	public $sutta_text_url_link;
	public $sutta_acronym;
	public $alt_sutta_acronym;
	public $biblio_entry_text;
}

class Reference
{
	public $language;
	public $text;
	public $url;
	
}

class Parallel
{
	public $id;
	public $uid;
	public $is_origin;
	public $acronym;
	public $alt_acronym;
	public $name;
	public $volpage_info;
	public $alt_volpage_info;
	public $text_url_link;
	public $footnote_text;
	public $collection_id;
	public $collection_language;
	public $biblio_entry_text;
	public $is_partial;
}
?>
