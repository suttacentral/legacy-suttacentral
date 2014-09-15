/* The sidebar class is responsible for everything in the aside navigation
 * menu / controls found in texts. presently this is displayed as a
 * side bar.
 */
sc.sidebar = {
    init: function() {
        var self=this;
        self.node = $('#sidebar');
        $('#toc').remove();
        if ($('#text').length > 0) {
            $('#toc').remove();
        } else {
            return
        } 
        /* TEMPORARY */
        $('#text').find('.next, .previous, .top').remove();
        /* END TEMPORARY */
        
        this.doMenu('#navigation-tab > .inner-wrap');
        this.doMetadata('#metadata-tab > .inner-wrap');
        $('#sidebar').show().easytabs({
            animate: false,
            tabs: '.tabs > li',
            updateHash: false
        });

        $('#sidebar').on('easytabs:before', function(e, $clicked, $target){
            sc.userPrefs.setPref('sidebar-selected-tab', $target.attr('id'));
        });
        
        $('#sidebar-dongle').on('click',
            function(){
                if (self.isVisible()) {
                    self.hide();                        
                } else {
                    self.show();
                }
                return false
            }
        );
        $('#sidebar').on('click', function(e){
            if (!$(e.target).is('div')) return true;
            self.hide();
        });
        self.bindButtons();
        scState.save("clean");

        if ($.cookie('t-line-by-line')) {
            self.toggleLineByLine();
        }
        
    },
    isVisible: function() {
        return this.node.hasClass('active');
    },
    show: function() {
        this.node.addClass('active');
        sc.userPrefs.setPref('sidebar', true);
    },
    hide: function() {
        this.node.removeClass('active');
        sc.userPrefs.setPref('sidebar', false);
    },
    selectTab: function(tab) {
        this.node.easytabs('select', '#' + tab);
    },
    bindButtons: function(){
        $('#text-info').click(toggleTextualInfo);
        $('#pali-lookup').click(togglePaliLookup);
        for (f in transFuncs) {
            $('#' + f).click(transliterateHandler);
        }
        $('#lookup-to-lang').change(function(){
            sc.userPrefs.setPref('lookupToLang', $(this).val());
            if (sc.userPrefs.getPref("paliLookup") === true) {
                sc.init(true);
            }            
        });
        $('#t-line-by-line').click(this.toggleLineByLine);
        this.initChineseLookup();

    },
    toggleLineByLine: function(e) {
        var brs = $('br.t-br');
        if (brs.length) {
            brs.remove();
            $('#text').removeClass('line-by-line');
            $.removeCookie('t-line-by-line');
        } else {
            $('.t').before('<br class="t-br">');
            $('br + br.t-br').remove();
            $('#text').addClass('line-by-line');
            $.cookie('t-line-by-line', 1)
        }
        
    },
    initChineseLookup: function() {
        if ($('#zh2en').length == 0) return;
        //Where to attach the chinese lookup control button.
        sc.zh2enLookup.init('#zh2en', '#text');
    },
    disableControls: function(){
        $('#textual-controls button').attr('disabled', 'disabled');
    },
    enableControls: function() {
        $('#textual-controls button').removeAttr('disabled');
    },
    doMenu: function(target, headings){
        var self = this,
            start = Date.now()
        
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
                existingAnchor.attr({href: "#table-of-contents"});
            } else {
                $(this).wrapInner('<a id="{}" href="#table-of-contents" />'.format(ref))
            }

        });
        if (menu.length > 1) {
            menu.push('</ul>');
            $('<div id="table-of-contents">').append(menu.join('')).appendTo(target);
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
    messageBox: {
        show: function(message, args) {
            // Eliminate faded out elements.
            $('#message-box .message:hidden').remove();
            args = args || {};
            var msgObj = $('<div class="message"><a class="remove" onclick="$(this).parent().fadeOut(); return true;">×</a>').append(message).attr('id', args.id);
            $('#message-box').append(msgObj);
            if (args.timeout) {
                setTimeout(function(){
                    msgObj.fadeOut();                
                }, args.timeout)
            }

        },
        remove: function(id) {
            $('#message-box').find('[id="' + id + '"]').fadeOut();
        },
        clear: function(){
            $('#message-box > .message').fadeOut();
        }
    }
}

