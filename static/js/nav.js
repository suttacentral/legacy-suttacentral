// AJAX search results.
var sc_nav = {
    search_element: $('#page-header-search > input'),
    search_results: $('#page-header-search-results'),
    lastXHR: null,
    init: function() {
        sc_nav.search_element.keyup(sc_nav.handleSearch);
        $('body').mousedown(sc_nav.hideResultsIfNotSearch);
    },
    handleSearch: function(e) {
        var input = e.target.value;
        if (sc_nav.lastXHR) {
            sc_nav.lastXHR.abort();
        }
        if (input.length < 3) {
            sc_nav.hideResults();
            return;
        }
        url = "/search?query=" + encodeURIComponent(input) + "&ajax=1";
        ajax = jQuery.ajax(url, { "cache": "true" });
        ajax.done(sc_nav.done);
        sc_nav.lastXHR = ajax;
    },
    done: function(data, code, jqXHR) {
        results = $("<div>" + data + "</div>");
        sc_nav.search_results.html(results);
        sc_truncate.apply(sc_nav.search_results, 125);
        sc_nav.search_results.find("tr").filter(":even").addClass("even");
        $("span.precision").attr({'title': 'Estimated precision of location, 1 = very certain.'});
        sc_nav.showResults();
    },
    hideResultsIfNotSearch: function(e) {
        var target = $(e.target);
        if (!target.closest('#page-header-search')[0] &&
            !target.closest('#page-header-search-results')[0]) {
            sc_nav.hideResults();
        }
    },
    hideResults: function() {
        sc_nav.search_results.stop(true, true).slideUp();
    },
    showResults: function() {
        sc_nav.search_results.stop(true, true).slideDown();
    }
};

sc_nav.init();

//This code powers the 'more' and 'less' functionality. I checked out
//jquery.truncator and jquery.expander but they didn't do what I wanted.

// There are two usages. First, the server can deliver HTML which has a
// structure like so: 
/*
 <li> <--or div, or any block level element-->
   <div class="showless" style="display:none">Brief <a href="showmore"></a></div>
   <div class="showmore">Entry in full <a href="showless"></a></div>
 </li>
*/

// To help those who have JS disabled, 'showmore' needs to be visible
// and 'showless' hidden by default, this need not be done with AJAX content
// since AJAX by definition requires javascript.

// In the other usage, simply deliver the full content, and give anything which
// should be truncated class="truncate". If this is delivered by AJAX, you must
// call sc_truncate.apply on a containing element.

// To reduce bugapossabilities the auto-generated brief is based on the plain
// text rendering of the full content and internally the following four selectors
// are used and reserved:
// div.showmore, div.showless, a.showmore, a.showless

sc_truncate = {
    init: function(max_length){
        this.apply(document.body, max_length);
    },
    apply: function(target, max_length){
        if (!max_length) max_length = 200;
        $(target).find('.truncate').each(function(){
            if ($(this).find('div.showmore, div.showless').length > 0) {
                return
            }

            var brief = sc_truncate.brief(this, max_length);
            if (brief===false) return; // No enbriefing needed.
            var parent = $(this).parent()
            var showmore = $('<div class="showmore"/>').appendTo(parent);
            showmore.append(this);
            var showless = $('<div class="showless"/>').html(brief).appendTo(parent);
            showmore.find('p:last').append('<a class="showless"></a>');
            showless.append('<a class="showmore"></a>');
            showmore.hide();
        });
        $('div.showless').show();
        $('div.showmore').hide();
        $('a.showless').text('[less]');
        $('a.showmore').text('[…more]');
    },
    brief: function(element, max_length) {
        //may return text or html
        var text = $(element).text();
        if (text.length < max_length) {
            //Nothing to do.
            return false
        }
        var brief = text
        //Remove references which contain a number:
        brief = brief.replace(/(^| )(?=[a-zA-Z.]*\d)([^, ]+)/g, '');
        brief = brief.replace(/\s{2,}/g, ' ') //Normalize whitespace
        brief = brief.slice(0, max_length + 1);
        var m = brief.match(/.*\./);
        if (m && m[0].length > max_length * 3 / 4) {
            brief = m[0];
        } else {
            //Remove trailing characters, which might be a broken word:
            brief = brief.replace(/[^ —,.]*$/, '')
        }
        return brief
    },
}

sc_truncate.init();

$(document.body).on('click', 'a.showmore', function() {
    parent = $(this).parent().parent();
    parent.children('div.showless').slideUp();
    parent.children('div.showmore').slideDown();
    parent.find('a.showless').each(function(){
        // Move the 'show less' link to its proper place
        parent.find('div.showmore p:last').append(this);
    });
    return false
});

$(document.body).on('click', 'a.showless', function() {
    parent = $(this).parents('div.showmore').parent();
    showless = parent.children('div.showless').show();
    parent.children('div.showmore').hide();
    scrollto = parent.find(':first')[0]
    // I was offline when writing this and not sure it's the best way.
    scrollto.scrollIntoView();
    
    
    return false
});