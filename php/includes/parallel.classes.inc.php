<?php
include_once $_SERVER["DOCUMENT_ROOT"]."/includes/db.inc.php";

// Instances of this class are created by the ParallelFactory class.
// Given an "origin", the sutta we are finding parallels for, we
// can access the full parallels and partial parallels.
class ParallelCollection
{
	// The id of the sutta we are finding parallels for.
	public $origin = "";
	// The sutta ids for all full parallels of origin.
	public $full = array();
	// The sutta ids for all partial parallels of origin.
	public $partial = array();
	// A map of suttas to footnotes.
	public $footnotes = array();
	
	// Always called when we create a new collection object.
	public function __construct($origin)
	{
		$this->origin = $origin;
	}
	
	// This exists simply for debugging purposes.
	public function printOut()
	{
		echo "Origin: " . $this->origin . "<br>";
		echo "Full parallels(" . count($this->full) . "): ";
		foreach($this->full as $aFull)
		{
			echo $aFull . " ";
		}
		echo "<br>";
		echo "Partial parallels(" . count($this->partial) . "): ";
		foreach($this->partial as $aPartial)
		{
			echo $aPartial . " ";
		}
	}
	
	// Add a new full parallel for the origin sutta.
	// This is always done by the ParallelFactory class.
	public function addFull($parallel, $footnote)
	{
		// If the parallel already exists in the list of
		// full correspondence or is the origin itself
		// we can ignore it.
		if(in_array($parallel, $this->full) == false && 
		   $this->origin != $parallel)
		{
			$this->full[] = $parallel;
			$this->footnotes[$parallel] = $footnote;
		}
	}
	
	// Add a new partial parallel for the origin sutta.
	// This is always done by the ParallelFactory class.
	public function addPartial($parallel, $footnote)
	{
		// If the parallel already exists in the list of
		// partial correspondence or is the origin itself
		// we can ignore it.
		if(in_array($parallel, $this->partial) == false && 
		   $this->origin != $parallel)
		{
			$this->partial[] = $parallel;
			$this->footnotes[$parallel] = $footnote;
		}
	}
}

// This is a data access class that provides a few
// queries for dealing with the Correspondence table
// in the database.
class CorrespondenceTable
{
	// Given an sql statement in string format we
	// return an array of rows that result from 
	// that SQL query.
	function fetchRows($sql)
	{
		$result = mysql_query($sql);
		
		$found = array();
		
		while($row = mysql_fetch_assoc($result))
		{
			$found[] = $row;
		}
		
		return $found;
	}
	
	// Get all rows where the correspondence is full
	// and the sutta id is found in the entry_id column.
	function getEntryIdFullRows($sutta_id)
	{
		$sql = "SELECT * FROM correspondence 
				WHERE entry_id = '$sutta_id'
				AND partial_corresp_ind = 'N'";
		
		return $this->fetchRows($sql);
	}
	
	// Get all rows where the correspondence is full
	// and the sutta id is found in the corresp_entry_id column.
	// No results for sutta #16. Good to test this further.
	function getCorrespEntryIdFullRows($sutta_id)
	{
		$sql = "SELECT * FROM correspondence 
				WHERE corresp_entry_id = '$sutta_id'
				AND partial_corresp_ind = 'N'";
				
		return $this->fetchRows($sql);
	}
	
	// Get all rows where the correspondence is partial
	// and the sutta id is found in the entry_id column.
	function getEntryIdPartialRows($sutta_id)
	{
		$sql = "SELECT * FROM correspondence 
				WHERE entry_id = '$sutta_id'
				AND partial_corresp_ind = 'Y'";
		
		return $this->fetchRows($sql);
	}
	
	// Get all rows where the correspondence is partial
	// and the sutta id is found in the corresp_entry_id column.
	function getCorrespEntryIdPartialRows($sutta_id)
	{
		$sql = "SELECT * FROM correspondence 
				WHERE corresp_entry_id = '$sutta_id'
				AND partial_corresp_ind = 'Y'";
				
		return $this->fetchRows($sql);
	}
	
}

// This class knows about both the database (CorrespondenceTable)
// and the domain object ParallelCollection. Neither of these two
// classes know about each other. It is the factory's job to 
// retrieve the appropriate data and return a complete domain 
// object when the method makeCollection() is called. The client
// of ParallelFactory needs only to construct the object and
// call makeCollection() with the origin sutta id.
class ParallelFactory
{
	public $table;
	
	public function __construct()
	{
		$this->table = new CorrespondenceTable();
	}
	
	private function addFullParallels($collection)
	{
		// Retrieve all the rows for full correspondence where
		// the entry_id field is the origin.
		$entryIdFullRows = 
			$this->table->getEntryIdFullRows($collection->origin);
		
		// For each of these rows add the corresp_entry_id value 
		// as full correspondence to the parallel collection.
		foreach($entryIdFullRows as $entryIdFullRow)
		{
			$collection->addFull($entryIdFullRow['corresp_entry_id'],
								 $entryIdFullRow['footnote_text']);
		}
		
		// Now do the reverse. Get the full correspondence where
		// the origin is in the corresp_entry_id field.
		$correspEntryIdFullRows = 
			$this->table->getCorrespEntryIdFullRows($collection->origin);
		
		// And again do the reverse, adding the entry_id field of
		// the rows retrieved to the full collection.
		foreach($correspEntryIdFullRows as $correspEntryIdFullRow)
		{
			$collection->addFull($correspEntryIdFullRow['entry_id'],
								 $correspEntryIdFullRow['footnote_text']);
		}
		// When A is a full parallel of B and C is a full parallel of
		// B, then A is a full parallel of A. The following code finds
		// these secondary full correspondence.
		foreach($collection->full as $full)
		{
			// Start in the entry_id field.
			$secondaryEntryIdFullRows = 
				$this->table->getEntryIdFullRows($full);
			
			foreach($secondaryEntryIdFullRows as $secondaryEntryIdFullRow)
			{
				$collection->addFull($secondaryEntryIdFullRow['corresp_entry_id'],
									 $secondaryEntryIdFullRow['footnote_text']);
			}
			
			// Now do the same for the corresp_entry_id field.
			$secondaryCorrespEntryIdFullRows = 
				$this->table->getCorrespEntryIdFullRows($full);
				
			foreach($secondaryCorrespEntryIdFullRows as $secondaryCorrespEntryIdFullRow)
			{
				$collection->addFull($secondaryCorrespEntryIdFullRow['entry_id'],
									 $secondaryCorrespEntryIdFullRow['footnote_text']);
			}
		}
	}
	
	// This function adds any immediate partials to the collection.
	// An immediate partial is one where the origin is in the same 
	// row as the corresponding partial.
	private function addPartialOfOrigin($collection)
	{
		// Do the left hand side (origin is in the entry_id).
		$entryIdOriginPartialRows = 
			$this->table->getEntryIdPartialRows($collection->origin);
			
		// Add our results to the collection.
		foreach($entryIdOriginPartialRows as $entryIdOriginPartialRow)
		{
			$collection->addPartial($entryIdOriginPartialRow['corresp_entry_id'],
									$entryIdOriginPartialRow['footnote_text']);
		}
		
		// Now the right hand side (origin is in the corresp_entry_id).
		$correspEntryIdOriginPartialRows = 
			$this->table->getCorrespEntryIdPartialRows($collection->origin);
			
		// Again add the results to the collection.
		foreach($correspEntryIdOriginPartialRows as $correspEntryIdOriginPartialRow)
		{
			$collection->addPartial($correspEntryIdOriginPartialRow['entry_id'],
									$correspEntryIdOriginPartialRow['footnote_text']);
		}
	}
	
	// When A is a full parallel of B and C is a partial 
	// parallel of B then C is an "implied partial" of A.
	private function addPartialOfFull($collection)
	{
		// Iterate over the full parallels found so far.
		foreach($collection->full as $aFullParallel)
		{
			// Do the left hand side.
			$entryIdPartialRows = 
				$this->table->getEntryIdPartialRows($aFullParallel);
			
			foreach($entryIdPartialRows as $entryIdPartialRow)
			{
				$collection->addPartial($entryIdPartialRow['corresp_entry_id'],
									    $entryIdPartialRow['footnote_text']);
			}
			
			// Do the right hand side.
			$correspEntryIdPartialRows = 
				$this->table->getCorrespEntryIdPartialRows($aFullParallel);
				
			foreach($correspEntryIdPartialRows as $correspEntryIdPartialRow)
			{
				$collection->addPartial($correspEntryIdPartialRow['entry_id'],
										$correspEntryIdPartialRow['footnote_text']);
			}
		}
	}
	
	// When A is a partial parallel of B and C is a full 
	// parallel of B then C is an "implied partial" of A.
	private function addFullOfPartial($collection)
	{
		// Iterate over the partial parallels found so far.
		foreach($collection->partial as $aPartialParallel)
		{
			// Do the left hand side.
			$entryIdFullRows = 
				$this->table->getEntryIdFullRows($aPartialParallel);
			
			foreach($entryIdFullRows as $entryIdFullRow)
			{
				$collection->addPartial($entryIdFullRow['corresp_entry_id'],
										$entryIdFullRow['footnote_text']);
			}
			
			// Do the right hand side.
			$correspEntryIdFullRows = 
				$this->table->getCorrespEntryIdFullRows($aPartialParallel);
			
			foreach($correspEntryIdFullRows as $correspEntryIdFullRow)
			{
				$collection->addPartial($correspEntryIdFullRow['entry_id'],
										$correspEntryIdFullRow['footnote_text']);
			}
		}
	}

	private function addPartialParallels($collection)
	{
		// Add the direct partials
		$this->addPartialOfOrigin($collection);
		// Add the implied partials.
 		//$this->addPartialOfFull($collection);
 		//$this->addFullOfPartial($collection);
 		
	}
	
	public function makeCollection($origin)
	{
		$collection = new ParallelCollection($origin);
		$this->addFullParallels($collection);
		$this->addPartialParallels($collection);
		return $collection;
	}
}

class ParallelDetails
{
	private $collection;     // The collection for which we gather the details.
	private $parallelsTable; // A table of data with a row for each sutta.
	
	// Collect all the information needed for 
	// an individual sutta that is a parallel.
	private function fetchSuttaDetails($fullParallel)
	{
		$sql = "SELECT sutta.sutta_id,
				sutta.sutta_name,
				sutta.subdivision_id,
				sutta.sutta_number,		
				sutta.sutta_acronym,
				sutta.alt_sutta_acronym,
				sutta.volpage_info,
				sutta.alt_volpage_info,
				sutta.sutta_text_url_link,
				collection_language.collection_language_id,
				collection_language.collection_language_name,
				biblio_entry.biblio_entry_text
				FROM sutta 
				INNER JOIN collection_language 
					ON sutta.collection_language_id = collection_language.collection_language_id	
				LEFT JOIN biblio_entry 
					ON sutta.biblio_entry_id = biblio_entry.biblio_entry_id 
				WHERE sutta.sutta_id = '$fullParallel'";
				
		$result = mysql_query($sql) or die ('Query failed because: ' . mysql_error());
		$row = mysql_fetch_assoc($result);
		
		$details = array();
		$details['sutta_id'] = $row['sutta_id'];
		$details['sutta_name'] = $row['sutta_name'];
		$details['subdivision_id'] = $row['subdivision_id'];
		$details['sutta_number'] = $row['sutta_number'];
		$details['sutta_acronym'] = $row['sutta_acronym'];
		$details['alt_sutta_acronym'] = $row['alt_sutta_acronym'];
		$details['volpage_info'] = $row['volpage_info'];
		$details['alt_volpage_info'] = $row['alt_volpage_info'];
		$details['sutta_text_url_link'] = $row['sutta_text_url_link'];
		$details['collection_language_id'] = $row['collection_language_id'];
		$details['collection_language_name'] = $row['collection_language_name'];
		$details['biblio_entry_text'] = $row['biblio_entry_text'];
		
		return $details;
	}
	
	private function makeParallelsTable()
	{
		$this->parallelsTable = array();
		
		// As per Bhante Sujato's request the origin is added
		// to the list along with it's parallels. This avoids
		// clutter in the caption. TODO Add bug reference.
		$parallelDetails = $this->fetchSuttaDetails($this->collection->origin);
		$parallelDetails['is_origin'] = true; // Used for sorting.
		$parallelDetails['is_partial'] = 'N';
		$parallelDetails['footnote_text'] = "";
		$this->parallelsTable[] = $parallelDetails;
		foreach($this->collection->full as $fullParallel)
		{
			$parallelDetails = $this->fetchSuttaDetails($fullParallel);
			$parallelDetails['is_origin'] = false; 
			$parallelDetails['is_partial'] = 'N';
			$parallelDetails['footnote_text'] = $this->collection->footnotes[$fullParallel];
			$this->parallelsTable[] = $parallelDetails;
		}
		
		foreach($this->collection->partial as $partialParallel)
		{
			$parallelDetails = $this->fetchSuttaDetails($partialParallel);
			$parallelDetails['is_origin'] = false; 
			$parallelDetails['is_partial'] = 'Y';
			$parallelDetails['footnote_text'] = $this->collection->footnotes[$partialParallel];
			$this->parallelsTable[] = $parallelDetails;
		}
	}
	
	private function sortParallelsTable()
	{
		if(count($this->parallelsTable) == 0) return;
		
		foreach($this->parallelsTable as $key => $row)
		{  
			$origin[$key]=$row['is_origin'];
			$language_id[$key]=$row['collection_language_id'];
		   $partial[$key]=$row['is_partial'];
		   $subdiv[$key]=$row['subdivision_id'];
		   $number[$key]=$row['sutta_number'];
		}

		array_multisort($origin, SORT_DSC,
						$language_id, SORT_ASC, 
						$partial, SORT_ASC, 
						$subdiv, SORT_ASC, 
						$number, SORT_ASC, 
						$this->parallelsTable);
	}
	
	public function __construct($collection)
	{
		$this->collection = $collection;
		$this->makeParallelsTable();
		$this->sortParallelsTable();
	}
	
	public function getListOfParallels()
	{
		$list = array();
		
		foreach($this->parallelsTable as $details)
		{
			$parallel = new Parallel();
			
			$parallel->id = $details['sutta_id'];
			$parallel->acronym = $details['sutta_acronym'];
			$parallel->alt_acronym = $details['alt_sutta_acronym'];
			$parallel->name = $details['sutta_name'];
			$parallel->volpage_info = $details['volpage_info'];
			$parallel->alt_volpage_info = $details['alt_volpage_info'];
			$parallel->text_url_link = $details['sutta_text_url_link'];
			$parallel->footnote_text = $details['footnote_text'];
			$parallel->collection_language_id = $details['collection_language_id'];
			$parallel->collection_language = $details['collection_language_name'];
			$parallel->biblio_entry_text = $details['biblio_entry_text'];
			$parallel->is_origin = $details['is_origin'];
			
			if($details['is_partial'] == 'Y') 
			{
				$parallel->is_partial = true;
			}
			else
			{
				$parallel->is_partial = false;
			}
			
			$list[] = $parallel;
		}
		
		return $list;
	}
}
?>
