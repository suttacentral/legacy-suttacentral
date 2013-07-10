sc_nav = {
    search_element: document.getElementsByName("query")[0],
    lastXHR: null,
    init: function(){
        this.search_element.oninput = sc_nav.handleSearch;
        this.search_element.onmouseover = sc_nav.handleSearch;
    },
    ready: function(){

    },
    handleSearch: function(e) {
        var input = e.target.value;
        if (sc_nav.lastXHR)
            sc_nav.lastXHR.abort();
        if (input.length < 2) {
            $("#search_results").hide().html("");
            return;
        }
        url = "/search?query=" +input+"&ajax=1";
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
    },
};

sc_nav.init();