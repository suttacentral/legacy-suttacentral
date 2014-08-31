//Shims
if (String.prototype.trimLeft === undefined)
{
    String.prototype.trimLeft = function() {
        return this.replace(/^\s+/,"");
    }
}

sc.formatter = {
    //Designed to workaround limitations in css.
    init: function() {//Init is called only once.
        //$("body").on("mouseover", "span.lookup", function(e){sc.formatter.rePosition($(e.target))})
        $(window).resize(function(){
            //sc.formatter.shove();
            
            //$("span.lookup").mouseenter(function(e){sc.formatter.rePosition($(e.target))});
        });
        $(document).on('keydown', sc.formatter.deathToTheBeast);
        setTimeout(this.navMenuFixer, 1000);
        this.apply();
        this.operaFix();
        this.highlightBookmark();
        this.toolsMagic();
        this.overlapperFixer();
        setTimeout(this.acro_expander, 500);
        $(window).resize(this.overlapperFixer);
    },
    apply: function(){
        $("tr").filter(":even").addClass("even"); //Add the .even class to every second tr element
        sc.formatter.quoteHanger();
        
    },
    shove: function(){
        var start = (new Date()).getTime();
        $("q").each(function(){sc.formatter.rePosition($(this))});
    },
    operaFix: function(){
        if ('opera' in window) {
            if ('version' in window.opera && window.opera.version > 12.2)
            {
                return;
            }
            $(document.body).addClass('badfonts');
        }
    },
    rePosition: function($element){
        return $element;
        var setLeft = false;
        var offset = $element.offset();
        var width = $element.innerWidth();
        if (offset.left < 1) {
            offset.left = 1;
            $element.offset(offset).innerWidth(width+1);
            //(width+1 is required for Chrome)
            setLeft = true;
        }
        if (offset.left + width > $(document).width())
        {
            offset.left = $(document).width() - (width + 2);
            $element.offset(offset).innerWidth(width+1);
        }
        return $element;
    },
    quoteHanger: function(){
        $('p').each(function(){
            children = this.childNodes
            node = this.childNodes[0];
            //Find the start of the actual text.
            if (!node) return;
            while (node.nodeType == 1) {
                if (node.nodeName == 'A') {
                    node = node.nextSibling
                }
                else {
                    node = nextInOrder(node);
                }
                if (!node) return;
            }
            if (node.nodeType == 3) {
                text = node.nodeValue.trimLeft()
                var firstChar = text[0];
                if (firstChar == '“' || firstChar == '‘')
                {
                    var secondChar = text[1];
                    if (secondChar == '“' || secondChar == '‘')
                    {
                        node.nodeValue = text.slice(2);
                        $(this).prepend('<span class="dsquo">' + firstChar + secondChar + '</span>');
                    } else {
                        node.nodeValue = text.slice(1);
                        if (firstChar == '‘') {
                            $(this).prepend('<span class="squo">' + firstChar + '</span>');
                        } else {
                            $(this).prepend('<span class="dquo">' + firstChar + '</span>');
                        }
                    }
                }
            }

        });
    },
    markOfTheBeast: 0,
    deathToTheBeast: function(event){
        if (event.which == 77 && event.ctrlKey == true)
        {
            if (!(window.scState && window.Iter)) return;
            
            textualControls.disable()
            var iter = new Iter(document.body, 'text');
            var startTime = Date.now();
            
            while (node = iter.next())
            {
                if (node.nodeValue)
                {
                    if (sc.formatter.markOfTheBeast % 2 == 0) {
                        node.nodeValue = node.nodeValue.replace(/ṃ/g, 'ṁ').replace(/Ṃ/g, 'Ṁ');
                    } else {
                        node.nodeValue = node.nodeValue.replace(/ṁ/g, 'ṃ').replace(/Ṁ/g, 'Ṃ');
                    }
                }
            }
            textualControls.enable();
            if (sc.formatter.markOfTheBeast % 2 == 0) {
            } else {
                var num = 1 + Math.ceil(sc.formatter.markOfTheBeast / 2);
                var suffix = 'th';
                if (num % 10 == 1 && num % 100 != 11) suffix = 'st';
                if (num % 10 == 2 && num % 100 != 12) suffix = 'nd';
                if (num % 10 == 3 && num % 100 != 13) suffix = 'rd';
            }
            sc.formatter.markOfTheBeast += 1
        }
    },
    highlightBookmark: function() {
        // Highlight the elements that are bookmarked.
        // If these elements contain a 'data-also-ids' those
        // elements (comma seperated) are also highlighted.
        var toHighlight = [window.location.hash], i=0;
        while (i < toHighlight.length)
        {
            e = $(toHighlight[i].replace(/\./g, '\\.'));
            if (e.length > 0) {
                e.addClass('bookmarkeded');
                alsoIds = e.attr('data-also-ids');
                if (alsoIds){
                    ids = alsoIds.split(/,\s*/g);
                    for (j in ids) {
                        toHighlight.push('#' + ids[j]);
                    }
                }
            }
            i++;
            if (i > 100) return;
        }
    },
    toolsMagic: function(){
        if ($('.tools').length == 0) {
            return
        }
        
        $('[data-allowed]').on('change', function(e){
            var filename = this.value,
                types = $(this).attr('data-allowed').split(' ,'),
                m = filename.match('.+[.](.+)');
            
            if (m && types.indexOf(m[1].toLowerCase()) != -1) {
                return
            }
            
            this.value = null;
            
            if (!m) {
                alert('Unknown filetype, only {} allowed'.format(
                    types.join(', ')));
            }
            else {
                alert('Filename extension .{} not allowed, only .{} allowed'.format(
                    m[1].toLowerCase(), types.join(', .')));
            }
        });
        
        tidy = {
            tidy: $('[value=html5tidy]'),
            level: $('[name=tidy-level]'),
            extra: $('#tidy-extra input'),
            flags: $('[name=tidy-flags]'),
            updateFlags: function(e){
                var self=tidy, 
                    flags = [];
                if (self.tidy[0].checked) {
                    $('#tidy ul input, #tidy textarea').removeAttr('disabled');
                } else {
                    $('#tidy ul input, #tidy textarea').attr('disabled', 'disabled');
                }
                
                flags.push(self.tidy.attr('data-flags'));
                for (var i = 0; i < self.level.length; i++){
                    flags.push($(self.level[i]).attr('data-flags'));
                    if (self.level[i].checked)
                        break;
                }
                for (var i = 0; i < self.extra.length; i++) {
                    if (self.extra[i].checked)
                        flags.push($(self.extra[i]).attr('data-flags'));
                };
                
                self.flags.val(flags.join(' ').replace(/  +/g, ' ').trim())
            },
            init: function(){
                var self=this;
                $('#tidy input, [name=cleanup]').on('change', self.updateFlags);
                self.updateFlags();
            }
        }

        decruft = {
            decruft: $('[name=decruft]'),
            what: $('[name^=decruft-]'),
            discard: $('[name=decruft-discard]'),
            unwrap: $('[name=decruft-unwrap]'),
            update: function(e){
                var self=decruft,
                    selectors = [];
                for (var i = 0; i < self.what.length; i++) {
                    if (self.what[i].checked){
                        selectors.push(self.what[i].value);
                    }
                }
                self.discard.val(selectors.join(', '))
            },
            init: function(){
                this.update();
                this.what.on('change', this.update);
            
            }
        }

        $('[name=tidy-file]').on('change', function(e){
            var self=e.target;
            if (e.target.value.search(/\.zip$/i) == -1){
                self.value = null;
                alert('Only zip files are acceptable.', 'Go away');
                
            }
        });

        function updateBoundStatus(target) {
            var boundElements = $($(target).attr('data-bound'));
            if (target.checked) {
                boundElements.removeAttr('disabled')
            }
            else {
                boundElements.attr('disabled', 'disabled')
            }
        }

        $('[data-bound]').on('change', function(e){updateBoundStatus(this)});
        $(document).on('ready', function(){
            $('[data-bound]').each(function(){updateBoundStatus(this)});
        });
        
        $('[name=show]').on('change', function(e){
            $('.entry').show();
            if (e.target.value != 'all')
                $('.entry').not(e.target.value).hide();
        });
        
        if ($('#tidy').length)
            tidy.init();
        if ($('#decruft').length)
            decruft.init();
    },
    acro_expander: function(){
        /*$('#vinaya_parallels td')
            .filter(':nth-of-type(1)')
            .each(function(){
                var acro = $(this).text().replace('&nbsp;', ' '),
                    name = sc.util.acro_to_name(acro);
                
                $(this).attr('title', name)
            });*/
    },
    overlapperFixer: function(){
        /* Certain paragraph numbers exist in an overly dense state, it is a
         * non-trivial (perhaps impossible) task in css to avoid collisions
         * when using absolute positioning. Fortunately it is easy in js
         * to flag items which are colliding.
         *
         * For the moment we only care about two items overlapping
         * completely, not partially. It is enough for our purposes.
         *
         * The document must be given a chance to render before this
         * function is called.
        */

        
        
        var offenders = $('.t, .t-linehead');

        
        if (offenders.length > 50) {
            if (!this.firstTime) {
                offenders.filter(':even').hide();
                this.firstTime = true;
            }
            /* DISABLED FOR PERFORMANCE REASONS */
            return
        }
        
        $('.collides').removeClass('collides');
        setTimeout(function(){
            var seen = {};
            offenders.each(function(){
                var top = $(this).offset().top;
                if (top in seen){
                    $(this).addClass('collides');
                    seen[top] += 1;
                } else {
                    seen[top] = 1
                }
            });
        }, 25);
    },
    alignToParentMenu: function(ul){
        var parent = ul.parent()
    },
    navMenuFixer: function(){
        var bodyWidth = $(document.body).width(),
            self = sc.formatter;
        function checkOkay(ul){
            var ul = $(this);
            var width = ul.width(),
                offset = ul.offset(),
                leftExtent = offset.left + width;
            if (leftExtent > bodyWidth){
                var parent = ul.parent(),
                    newLeftOffset = parent.offset().left - width;
                if (newLeftOffset < 0){
                    newLeftOffset = bodyWidth - width - 4;                    
                }
                ul.offset({left: newLeftOffset});
            }
            ul.children().children('ul').each(checkOkay);
        }
        $('#page-header-menu > nav > ul').each(checkOkay);
        if (self.navMenuFixer.first == undefined) {
            $(window).resize(function(){
                $('#page-header-menu ul').removeAttr('style');
                self.navMenuFixer();
            });
            self.navMenuFixer.first = true;
        }
    }
}
sc.formatter.init();
