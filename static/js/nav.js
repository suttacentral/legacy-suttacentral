var sc_nav = {
    search_element: $('#search_box input'),
    lastXHR: null,
    init: function(){
        sc_nav.search_element.keypress(sc_nav.handleSearch)
                             .mouseover(sc_nav.handleSearch);
    },
    handleSearch: function(e) {
        var input = e.target.value;
        if (sc_nav.lastXHR)
            sc_nav.lastXHR.abort();
        if (input.length < 2) {
            $("#search_results").hide().html("");
            return;
        }
        url = "/find?ya=" +input+"&ajax=1";
        //console.log(url);
        ajax = jQuery.ajax(url,{"cache":"true"});
        ajax.done(sc_nav.done);
        sc_nav.lastXHR = ajax;
    },
    done: function(data, code, jqXHR)
    {
        sc_nav.showResults(data)
    },
    showResults: function(data)
    {
        if (!document.getElementById("search_results")){
            $('<div id="search_results"></div>').appendTo("header").hide();
            $("header").mouseleave(function(){$("#search_results").slideUp()});
        }
        results = $("<div>" + data + "</div>");
        tds = results.find("td:nth-of-type(4)")
        for (i = 0; i < tds.length; i++)
        {
            td = $(tds[i]);
            lastchild = td.children().last().clone();
            td.empty();
            td.append(lastchild);
        }
        $("#search_results").html(results).slideDown();
        $("#search_results tr").filter(":even").addClass("even");
    }
}; sc_nav.init();
/*
        
        var m;
        if (m = input.match(/^[A-Z]{3}/i))
        {
            show += suttaSearch({"en":input, "pi":input});
        }
        else if (m = input.match(/^(sn?)[._\\/-]?([0-9]+)?[._\\/-]?([0-9]+)?/i))
        {
            nikaya = "Samyutta Nikaya ";
            samyutta = m[2];
            sutta = m[3];


            show = "Samyutta Nikaya ";
            if (samyutta >= 1 && samyutta <= 56){
                if (samyutta) show += samyutta;
                if (sutta)
                show += suttaSearch({"id":"sn"+samyutta+"."+sutta});
            }
        }

        results = document.getElementById("nav_results");
        results.innerHTML = show;
        console.log(show);

        return false;
    }

function suttaSearch(args){
    for (a in args) args[a] = args[a].toLowerCase();
    var data = getSearchData();
    var out = "";
    var good = [];
    var notsogood = [];
    if (args.id) {
       val = data.byId[args.id];
       if (val)
       {
           good.push([data.byId[args.id].id, data.byId[args.id].en + " / " + data.byId[args.id].pi]);
       }
    }

    if (args.en)
    {
        for (s in data.byEn)
        {
            ind = s.indexOf(args.en);
            if (ind == -1) {}
            else if (ind == 0)
                good.push([data.byEn[s].id, data.byEn[s].en])
            else
                notsogood.push([data.byEn[s].id, data.byEn[s].en])
        }
    }
    if (args.pi)
    {
        for (s in data.byPi)
        {
            ind = s.indexOf(args.pi);
            if (ind == -1) {}
            else if (ind == 0)
                good.push([data.byPi[s].id, data.byPi[s].pi])
            else
                notsogood.push([data.byPi[s].id, data.byPi[s].pi])
        }
    }
    var results = good.concat(notsogood);
    for (i = 0; i < results.length; i++)
    {
        var m = results[i][0].match(/(sn)([0-9]+)\.([0-9]+)/);
        uri = m[1] + m[2] + ".html";
        mark = "#"+m[2] + "." + m[3];
        out += '<p><a href="'+uri+mark+'">'+results[i][0] + ". " + results[i][1]+'</a></p>';
    }
    return out;
}


var _searchData = null;
function getSearchData(){
    if (!_searchData)
    {
        _searchData = {"byId":{},"byPi":{},"byEn":{}}
        
        for (i = 0; i < samHeadMap.length; i++){
            _searchData.byId[samHeadMap[i][0].toLowerCase()] = {"id":samHeadMap[i][0], "pi":samHeadMap[i][1], "en":samHeadMap[i][2]};
            _searchData.byPi[samHeadMap[i][1].toLowerCase()] = {"id":samHeadMap[i][0], "pi":samHeadMap[i][1], "en":samHeadMap[i][2]};
            _searchData.byEn[samHeadMap[i][2].toLowerCase()] = {"id":samHeadMap[i][0], "pi":samHeadMap[i][1], "en":samHeadMap[i][2]};
        }
    }
    if (!_searchData) throw TypeError;
    return _searchData;
}
    
/*
<script language=”javascript” type=”text/javascript”>
2
window.location.href=”login.jsp?backurl=”+window.location.href;
3
</script>
2,

1
<script language=”javascript”>
2
alert(”back”);
3
window.history.back(-1);
4
</script>
3,

1
<script language=”javascript”>
2
window.navigate(”top.jsp”);
3
</script>
4,

1
<script language=”JavaScript”>
2
self.location=”top.htm”;
3
</script>
5,

1
<script language=”javascript”>
2
alert(”Access Violation”);
3
top.location=”error.jsp”;
4
</script>
*/
