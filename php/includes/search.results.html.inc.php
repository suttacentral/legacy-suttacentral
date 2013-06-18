<?php
    include_once $_SERVER["DOCUMENT_ROOT"]."/includes/division.db.inc.php";
    function basicSearchURL($what){
        return "/find?ya=$what";
    }
    $sort_key = "uid";
    function cmp($a, $b)
    {
        global $sort_key;
        if ($sort_key == "") $sort_key = "uid";
        if (!$a or !$b) return 0;

        $numa = preg_replace('/\D*([\d.]+).*/', '$1', $a->$sort_key);
        $numb = preg_replace('/\D*([\d.]+).*/', '$1', $b->$sort_key);

        if ($numa != "" && $numb != "") return strnatcmp($numa, $numb);
        return 0;
    }
    function merge_sort(&$array, $cmp_function) {
        // Arrays of size < 2 require no action.
        if (count($array) < 2) return;
        // Split the array in half
        $halfway = count($array) / 2;
        $array1 = array_slice($array, 0, $halfway);
        $array2 = array_slice($array, $halfway);
        // Recurse to sort the two halves
        merge_sort($array1, $cmp_function);
        merge_sort($array2, $cmp_function);
        // If all of $array1 is <= all of $array2, just append them.
        if (call_user_func($cmp_function, end($array1), $array2[0]) < 1) {
            $array = array_merge($array1, $array2);
            return;
        }
        // Merge the two sorted arrays into a single sorted array
        $array = array();
        $ptr1 = $ptr2 = 0;
        while ($ptr1 < count($array1) && $ptr2 < count($array2)) {
            if (call_user_func($cmp_function, $array1[$ptr1], $array2[$ptr2]) < 1) {
                $array[] = $array1[$ptr1++];
            }
            else {
                $array[] = $array2[$ptr2++];
            }
        }
        // Merge the remainder
        while ($ptr1 < count($array1)) $array[] = $array1[$ptr1++];
        while ($ptr2 < count($array2)) $array[] = $array2[$ptr2++];
        return;
    }
    function getSearchResults($query)
    {
        mb_internal_encoding("UTF-8");
        mb_regex_encoding("UTF-8");
        
        $q = mb_strtolower(mb_ereg_replace("'", "\\'", $query));
        $patt = array();
        $repl = array();
        $patt[0] = '/(([kgcjtd])\2?)/i';  $repl[0] = '$1h?';
        $patt[1] = '/a/i';                $repl[1] ='[a]{1,2}';
        $patt[2] = '/i/i';                $repl[2] ='[i]{1,2}';
        $patt[3] = '/u/i';                $repl[3] ='[u]{1,2}';
        $patt[4] = '/t/i';                $repl[4] ='[t]{1,2}';
        $patt[5] = '/d/i';                $repl[5] ='[d]{1,2}';
        $patt[6] = '/n/i';                $repl[6] ='[n]{1,2}';
        $patt[7] = '/m/i';                $repl[7] ='[m]{1,2}';
        $patt[8] = '/l/i';                $repl[8] ='[l]{1,2}';
        $patt[9] = '/([kgcjp])/i';        $repl[9] ='$1{1,2}';
        $patt[10] = '/[vb]y/i';           $repl[10] ='[vb]y';
        $namerex = preg_replace('/([\[\]\(\)\*\+\.\?\$\^])/', '\\\\\\$1', $q);

        $namerex = preg_replace($patt, $repl, $namerex); // preg seems to deal with utf-8 here okay.
        
        $sql = "SELECT sutta.sutta_id,
                    sutta.sutta_uid,
                    sutta.sutta_acronym,
                    sutta.alt_sutta_acronym,
                    sutta.sutta_name,
                    sutta.sutta_plain_name,
                    sutta.sutta_coded_name,
                    sutta.volpage_info,
                    sutta.alt_volpage_info,
                    sutta_text_url_link
                FROM  sutta
                WHERE  sutta_uid LIKE '%$q%'
                    OR sutta_acronym LIKE '%$q%'
                    OR sutta.alt_sutta_acronym LIKE '%$q%'
                    OR sutta_name LIKE '%$q%'
                    OR sutta_plain_name REGEXP '$namerex'
                    OR sutta_coded_name LIKE '%$q%'
                    OR volpage_info LIKE '%$q%'
                    OR sutta.alt_volpage_info LIKE '%$q%'
                LIMIT 0, 10000";

        $results = mysql_query($sql) or die ('Query failed in : getSuttasInDivision()' . mysql_error());
        
        //Best quality comes first.
        $tiers = array(array(), array(), array(), array(), array(), array(), array());
        $sort_keys = array();

        while($row = mysql_fetch_assoc($results))
        {
            $quality = 9;
            $reverse_row = array_reverse($row);
            
            foreach ($reverse_row as $table => &$value)
            {
                if (mb_strtolower($value) == $q)
                {
                    $quality = 0;
                    $sort_keys[$quality] = $table;
                    break;
                }
                $pos = mb_stripos($value, $q);
                if ($pos === 0)
                {
                    if ($value[$pos + mb_strlen($q)] == ' ')
                    {
                        $quality = min($quality, 1);
                    } else {
                        $quality = min($quality, 2);
                    }
                    $sort_keys[$quality] = $table;
                }
                elseif ($pos > 0)
                {
                    if ($value[$pos + mb_strlen($q)] == ' ' && $value[$pos-1] == ' ')
                    {
                        $quality = min($quality, 2);
                    } else {
                        $quality = min($quality, 3);
                    }
                    $sort_keys[$quality] = $table;
                }
                else {
                    if (mb_eregi($namerex, $value, $match)){
                        $pos = mb_stripos($value, $match[0]);

                        if ($pos == 0)
                        {
                            $quality = min($quality, 4);
                            $sort_keys[$quality] = $table;
                        } else {
                            $quality = min($quality, 5);
                            $sort_keys[$quality] = $table;
                        }
                    }
                }
            }

            if ($quality == 9) next;

            $sutta_id = $row["sutta_id"];
            $sutta_uid = $row["sutta_uid"];
            $sutta_name = $row["sutta_name"];
            $sutta_acronym = $row["sutta_acronym"];
            $alt_sutta_acronym = $row["alt_sutta_acronym"];
            $volpage_info = $row["volpage_info"];
            $alt_volpage_info = $row["alt_volpage_info"];
            $sutta_text_url_link = $row["sutta_text_url_link"];

            $next_sutta = new Sutta();

            $tiers[$quality][] = $next_sutta;
            $next_sutta->id = $sutta_id;
            $next_sutta->uid = $sutta_uid;
            $next_sutta->name = $sutta_name;
            $next_sutta->sutta_acronym = $sutta_acronym;
            $next_sutta->alt_sutta_acronym = $alt_sutta_acronym;
            $next_sutta->volpage_info = $volpage_info;
            $next_sutta->alt_volpage_info = $alt_volpage_info;
            $next_sutta->sutta_text_url_link = $sutta_text_url_link;
        }

        foreach ($tiers as $quality => &$tier)
        {
            if ($tier != false) //ie is not empty
            {
                global $sort_key;
                $sort_key = $sort_keys[$quality];
                merge_sort($tier, "cmp");
            }
        }
        return array_merge($tiers[0], $tiers[1], $tiers[2], $tiers[3], $tiers[4], $tiers[5]);
    }
    $allResults = getSearchResults($q);
    $suttas = array_slice($allResults, $from, $range);
    

?>

<table>
<caption><?php
    if (empty($suttas)){
        $nothing = array("natthi", "na kiñci", "nothing");
        $nothing = $nothing[rand(0, count($nothing) - 1)];
        echo "Results: <strong>Not found.</strong>";
    }
    else {
        $to = $from + count($suttas);
        $max = count($allResults);
        if (!$ajax && $from > 0) {
            $prev = max(0, $from - $range) ;
            echo " <a style=\"float:left\" href=\"". basicSearchURL($q) ."&from=$prev&range=$range\"> ◀ Results ".($prev+1)." to $from</a> ";
        }

        echo "Results for <strong>$q</strong>— <strong> ". ($from + 1) . " to $to</strong> of " . $max . ".";

        if (!$ajax && $to < $max) {
            $next = $from + $range;
            $nextMax = min($next + $range, $max);
            echo " <a style=\"float:right\" href=\"". basicSearchURL($q) ."&from=$next&range=$range\">Results ".($next+1)." to $nextMax  ▶ </a>";
        }
    }
?>
</caption>
<thead>
<tr>
<th>Identifier</th>
<th>Title</th>
<th>Vol/Page</th>
<th>Parallels</th>
<th class="transcol">Translations</th>
</tr>
</thead>

<tbody>
<?php

    include $_SERVER["DOCUMENT_ROOT"]."/includes/sutta.list.html.inc.php";

?>
</tbody>
</table>
<?php
    if ($ajax) {
        $url = basicSearchURL($q);
        echo "<a class=\"goto-all\" href=\"$url\">Go to full search results</a>";
    }
?>
