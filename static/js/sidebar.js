/* This code is responsible for constructing the sidebar */

sc.sidebar = {
    id: "sidebar",
    textInfoButtonId: "text_info_button",
    paliLookupButtonId: "pali_lookup_button",
    textualControls: {
        id: "textual_controls",
        marginClasses: "a.as, a.bl, a.bps, a.eno89, a.fuk03, a.fol, a.gatha-number, a.gatn, a.gbm, a.gno78, a.har04, a.hoe16, a.hos89a, a.hos89b, a.hos91, a.hs, a.kel, a.mat85, a.mat88, a.mit57, a.ms, a.ms-pa, a.of, a.pts, a.pts1, .pts2, a.pts-cs, a.pts-vp-en, a.pts-vp-pi, a.pts_pn, a.roth, a.san87, a.san89, a.sc, a.sen82, a.sht, a.snp-vagga-section-verse, a.snp-vagga-verse, a.t, a.titus, a.t-linehead, a.ud-sutta, a.ud-vagga-sutta, a.tri62, a.tri95, a.tu, a.uv, a.vai58, a.vai59, a.vai61, a.verse-num-pts, a.vimula, a.vn, a.wal48, a.wal50, a.wal52, a.wal55b, a.wal57c, a.wal58, a.wal59a, a.wal60, a.wal61, a.wal68a, a.wal70a, a.wal70b, a.wal76, a.wal78, a.wal80c, a.wp, a.yam72",
        popupClasses: ".pub, .var, .rdg, .cross, .end",
        contentClasses: ".supplied, .supplied2, .add, .corr, .del, .end, .lem, .sic, .surplus",
        metaarea: "#metaarea",
        init: function(){
            this.allInfoClasses = this.textInfoClasses + ", " + this.textmarginInfoClasses;
            if (document.getElementById(this.id)){
                document.getElementById(this.id).innerHTML = "";
            } else { //Create at the best position.
                controls = '<div id="' + this.id + '"></div>';
                if ($("#sidebar").append(controls).length) {}//Bottom of the #sidebar
                else if ($("#menu, menu").last().after(controls).length){}//Below the menu
                else if ($("#onecol").prepend(controls).length) {}//Start of the #onecol
                else if ($("header").last().after(controls).length) {}//Below the header
                else if ($("body").prepend(controls).length) {}//Start of the body
                else {
                    alert("Something seriously weird has happened! Failed to find anywhere to insert the textual controls. No #sidebar, no (#)menu, no header, not even a body! What kind of weird html document is this?");
                }
            }
            this.initChineseLookup();
            this.initPaliFunctions(); 
            $("#metaarea").detach().appendTo("#sidebar")
        },
        initChineseLookup: function() {
            //Logic for deciding whether to install chinese lookup
            if ($('div[lang*=zh]').length == 0) return;//no elements declared to be chinese
            if (!sc.zh2enLookup) return;

            //Where to attach the chinese lookup control button.
            sc.zh2enLookup.init('#' + sc.sidebar.id, '#text')
        },
        initPaliFunctions: function() {
            //Logic for deciding whether to install pali lookup
            if ($('div').filter($('[lang*="pi"]')).length > 0) sc.mode.pali = true

            //Create elements
            this.addButtons(document.getElementById(this.id));
        },
        addButtons: function(target) {
            if (!target) return;
            var out = ''
            if (sc.mode.pali === true){
                out += '<button id="' + paliLookupButtonId + '">Pali→English Dictionary</button>' + '<div id="' + paliLookupLogId + '"></div>';

                out += '<div id="translitButtons">';
                for (f in transFuncs) {
                    out += '<button id="' + f + '">' + transFuncs[f][1] + '</button>'
                }
                out += '</div>';
            }

            out += '<button id="' + sc.sidebar.textInfoButtonId + '">Textual Information</button>';

            $(target).append(out);
        },
        bindButtons: function(){
            document.getElementById(this.textInfoButtonId).onclick = toggleTextualInfo;
            if (sc.mode.pali === true){
                document.getElementById(sc.sidebar.paliLookupButtonId).onclick = togglePaliLookup;

                for (f in transFuncs) {
                    try {
                        document.getElementById(f).onclick = transliterateHandler;
                    } catch (e) {/*If button doesn't exist.*/}
                }
            }
        }
    },
    
    init: function(){
        this.textualControls.init();       
        scState.save("clean");
    },
    disable: function() {
        $('#' + this.id + ' button').attr('disabled', 'disabled');
    },
    enable: function() {
        $('#' + this.id + ' button').removeAttr('disabled');
    }
}

/* The sidebar class is responsible for everything in the aside navigation
 * menu / controls found in texts. presently this is displayed as a
 * side bar.
 */
sc.sidebar = {
    node: $('#sidebar'),
    init: function() {
        var self=this;
        $('#toc').remove();
        if ($('#text').length > 0) {
            $('#toc').remove();
        } else {
            return
        }
        this.doMenu('#contents-tab > .inner-wrap');
        this.doMetadata('#metadata-tab > .inner-wrap');
        this.node.show().easytabs({
            animate: false,
            tabs: '.tabs > li',
            updateHash: false
        });
        setTimeout(function(){
            self.node.removeClass('active');
        }, 500);
        $('#sidebar-dongle').on('click', function(){$('#sidebar').toggleClass('active'); return false});
        self.node.on('click', function(e){if ($(e.target).is('a, p')) return true; self.node.removeClass('active')});
        
    },
    generateTextualControls: function(){

    },
    doMenu: function(target, headings){
        var self = this;
        if ($('#menu ul').length) return; //Keep existing menu.
        
        var start = Date.now()
        if (!headings) {
            headings = $('#text').find('h2,h3,h4,h5,h6');
        }
        var patimokkhaUid = ($('section.sutta[id*=-pm]').attr('id'))
        if (patimokkhaUid) {
            // Use alternative heading regex which
            // displays numbered component.
            headrex = /(.*)/;
        } else {
            headrex = /[ivx0-9]{1,5}[.:] \(?([^(]+)/i;
        }
        
        adjustment = 6
        headings.each(function(){
            adjustment = Math.min(this.tagName.replace('H', '') - 1, adjustment)
        })
        menu = ['<ul>']
        currentDepth = 1
        seen = {null:1}
        headings.each(function(){
            depth = this.tagName.replace('H', '') - adjustment;
            while (depth > currentDepth) {
                menu.push('<li><ul>');
                currentDepth++;
            }
            while (depth < currentDepth) {
                menu.push('</ul></li>')
                currentDepth--;
            }
            headtext = $(this).text();
            m = headtext.match(headrex);
            if (m){
                menutext = m[0].trim();
            } else {
                menutext = headtext;
            }
            menutext = menutext.toTitleCase();
            
            var ref,
                existingAnchor = $(this).find('[id]').first();
            
            if (existingAnchor.length && existingAnchor.text()) {
                ref = existingAnchor.attr('id');
            } else {
                ref = $(this).attr('id');
                if (!ref){
                    var asciified = (sc.util.asciify(menutext.toLowerCase()) || menutext).replace(/ /g, '-'),
                        oref = ref = asciified;
                    while (ref in seen) {
                        ref = oref + ++i;
                    }
                }
            }
            
            menu.push('<li><a href="#{}">{}</a></li>'.format(ref, menutext));
            
            if (existingAnchor.length) {
                existingAnchor.attr({href: "#menu"});
            } else {
                $(this).wrapInner('<a id="{}" href="#menu" />'.format(ref))
            }

        });
        if (menu.length > 1) {
            menu.push('</ul>');
            $('<div id="menu">').append(menu.join('')).appendTo(target);
        }
        
        if (patimokkhaUid) {
            var isRule = /(?:pj|ss|an|np|pc|pd|sk|as)\d+/;
            $('h4').each(function(){
                var h4 = $(this),
                    id = h4.find('[id]').attr('id');
                if (!isRule.test(id)) return;
                href = '/{}_{}'.format(patimokkhaUid, id);
                h4.append('<a href="{}" class="details" title="Go to parallels page">▶</a>'.format(href))
            });
        }
    },
    doMetadata: function(target){
        $(target).append($('#metaarea'));
    },
    sidebarAmmender: function(){
        var textInfo = $('#sc_text_info').text();
        if (!textInfo) return;
        var data = JSON.parse(textInfo),
            details = $('<div id="links">'),
            dothtml = location.href.search(/\.html\b/) == -1 ? '' : '.html';
        
        /*if (data.subdivision_uid && data.subdivision_uid != data.division_uid) {
            details.append('<a title="Goto Subdivision Page" href="../../{}">▲</a>'.format(data.subdivision_uid));
        } else*/
        if (data.division_uid) {
            details.append('<a title="Go to Division Page" class="division" href="../{}{}">▲</a>'.format(data.division_uid, dothtml));
        }
        
        if (data.sutta_uid) {
            details.append('<a title="Go to Details Page" class="details" href="../{}{}">▶</a>'.format(data.sutta_uid, dothtml));
        }
        data.all_lang_codes.sort().forEach(function(lang_code){console.log(lang_code);
                if (lang_code == data.lang_code) return;
                details.append('<a href="../{}/{}{}">{}</a>'.format(lang_code, data.uid, dothtml, lang_code));
            });
        
        $('#sidebar').prepend(details);
    },
}

