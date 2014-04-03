/* No doubt there are libraries which do this task well, but I wrote
 * this when I had no internet access. It works well.
 */

function registerSortableTable(table, defaultColumn){
    if (!defaultColumn) defaultColumn = 1;
    var rowhead = $(table).find('tr').first();
    rowhead.find('td, th').each(function registerHead(){
        $(this).on('click', sortByColumn);
    }).css('color', 'grey');
    
    sortByColumn(null, rowhead.find('td').eq(defaultColumn));
}

function sortByColumn(e, td){
    start = Date.now();
    if (!td) td = this;
    
    var tr = $(td).parent(),
        table = tr.parents('table').first(),
        cellIndex = td.cellIndex,
        rows = table.find('tr').not(':first'),
        ascending = !!table.data('direction'),
        last = table.data('last');

    if (last == td) {
        ascending = !ascending;
        table.data('direction', ascending);
    } else {
        table.data('last', td);
    }

    $(last).css('color', 'grey');
    $(td).css('color', 'purple');
  
    rows.sort(function(a,b,c){
        function clean(s){
            var num = Number(s.match(/[\d.]+/));
            if (num) return num;
            return s; // Fallback on text, and in JS "0" == 0
        }
        var a = clean($(a).find('td').eq(cellIndex).text()),
            b = clean($(b).find('td').eq(cellIndex).text());
            d = 0;
        
        if (a > b) d = 1
        else if (a < b) d = -1;
        if (!ascending)
            d = -d;
        
        return d
    });
    
    table.find('tbody').append(rows);
    console.log(Date.now() - start)
}

registerSortableTable('table');
