//  # Shims
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
    getRuler: function() {
        if (!this.ruler) {
            this.ruler = $('<p style="position:fixed; margin-left: -1000px">')
                         .appendTo('#text article')
        }
        return this.ruler;
    },
    measureQueue: [],
    queueMeasure: function(toMeasure, callback, ruler) {
        var self=this,
            ruler = ruler || this.getRuler(),
            args = [];
        _.each(toMeasure, function(content){
            var e = $('<span style="position: absolute; visibility: hidden">');
            e.append(content);
            ruler.prepend(e);
            args.push([content, e]);
        });
        self.measureQueue.push([args, callback]);
    },
    doMeasure: function() {
        var deferred = [];
        this.measureQueue.forEach(function(t){
            var args = t[0],
                callback = t[1],
                measurements = [];
            args.forEach(function(arg){
                measurements[arg[0]] = arg[1].innerWidth();
            });
            deferred.push([callback, measurements])
        });
        deferred.forEach(function(t) {
            var callback = t[0],
                measurements = t[1];
            callback(measurements);
        });
        this.measureQueue = [];
        this.measureNum = null;
        this.quoteHangerEnd = new Date().getTime();
    },
    quoteHanger: function() {
        var self = this;
        this.quoteHangerStart = new Date().getTime();
        $('p').each(function(){
            var p = $(this),
                text = p.text(),
                m = text.match(/^[  \n0-9.-]*([“‘]+)(.)/);
            if (m) {
                var snip = m[2],
                    quoted = m[1] + m[2];
                self.queueMeasure([quoted, snip], function(result){
                    var diff = result[quoted] - result[snip];
                    p.css('text-indent', -diff + 'px');
                }, p);
            }
        });
        self.doMeasure();
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
