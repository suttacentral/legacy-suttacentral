// Display partially internationalized view

sc.intr = {
    lang: window.localStorage.getItem('sc.intr.lang') || 'en',
    run: function() {
        var self = this;
        $('.translations').each(function(i, div){
            
            var $div = $(div),
                id = "dropdown-" + (i + 1),
                $links = $div.find('.tran'),
                $trigger = $('<a href="#"/>'),
                $specialLang = $div.find('a:contains(' + self.lang + ')').first();
        
            $div.addClass('ready');    
            if ($specialLang.length) {
                $specialLang.addClass('special');
                $div.prepend($specialLang);
                if ($links.length == 1) {
                    
                    return
                }
            }
            $trigger.text($links.length + ' ▾')

            var $dropdown = $('<div class="dropdown dropdown-relative dropdown-tip dropdown-anchor-right"/>'),
                $dropdownPanel = $('<div class="dropdown-panel"/>');

            $trigger.attr('data-dropdown', '#' + id);
            $dropdown.attr('id', id);
            $trigger.dropdown('attach', '#' + id);

            $dropdownPanel.append($links);
            $dropdown.append($dropdownPanel);
            $div.append($trigger)
            $div.append($dropdown)
            if ($specialLang.length) {
                $div.prepend($specialLang.addClass('special'));
            } else {
                $div.prepend('<span class="tran special">  </span>')
            }
        });

        $('.divtable').on('click', '.tran', function(e) {
                self.setLang($(e.target).text())
            });
        self.addHasTrans();

        //anchors.parents('table').find('tr').not('.has-tran').addClass('not-has-tran');
    },
    setLang: function(lang) {
        this.lang = lang;
        window.localStorage.setItem('sc.intr.lang', lang);
    },
    switchLang: function(e) {
        var self = sc.intr,
            lang = $(e.target).text();
        self.setLang(lang);
        self.run();
    },
    getTransCounts: function(callback) {
        $.ajax('/data/translation_count,langs?lang=' + sc.intr.lang)
        .done(callback);
    },
    makeLangSwitcher: function(langs){
        var out = $('<span class="switcher"/>');
        for (key in langs) {
            if (!langs[key].root) {
                out.append('<a class="lang-switch" href="#' + key + '">' + key + '</a>');
            }
        }
        console.log(out);
        console.log(langs);
        return out
    },
    addHasTrans: function() {
        var self = sc.intr;

        this.getTransCounts(function(data){
            self.trCounts = data.translation_count;
            self.langs = data.langs;
            self.addLangNames();
            if (!self.lang) return
        
            var langSwitcher = self.makeLangSwitcher(self.langs);
            $('#panel .contents').each(function(){
                var firstNum = 0;
                
                $(this).find('a').each(function(){
                    var $a = $(this),
                        href = $a.attr('href'), 
                        uid = href ? href.slice(1) : null;

                    if (uid && self.trCounts[uid]) {
                        $a.attr('data-translation-count', self.trCounts[uid]);
                        if (firstNum == 0) {
                            firstNum = self.trCounts[uid]
                        }
                    } else {
                        $a.attr('data-translation-count', 0);
                    }
                });
                if (firstNum > 0) {
                    var $note = $('<div class="panel-note"/>');
                    $note.append('<a data-translation-count="' + firstNum + '"> </a> ');
                    $note.append(self.lang + ' translations</div>');
                    //$note.append(' — ' + langSwitcher.html());
                    //console.log(langSwitcher);
                    $(this).append($note);
                }
            });
        });
        $('#panel').on('click', '.lang-switch', self.switchLang);
    },
    addLangNames: function(){
        $('.translations .tran:not(.special)').each(function(i, tran) {
            var uid = $(tran).text();
            $(tran).wrapInner('<span class="iso_code">')
                 .append(' ' + sc.intr.langs[uid].name);
        });
    }
}

sc.intr.run()
