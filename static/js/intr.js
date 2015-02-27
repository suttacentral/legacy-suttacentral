// Display partially internationalized view

sc.intr = {
    lang: window.localStorage.getItem('sc.intr.lang') || 'en',
    run: function() {
        var self = this,
            divtable = $('.divtable');
        var anchors = $($('.tran:contains(' + self.lang + ')').get().reverse());

        $('.translations').each(function(i, div){
            
            var $div = $(div),
                id = "dropdown-" + (i + 1),
                $links = $div.find('.tran'),
                $trigger = $('<a href="#"/>'),
                $specialLang = $div.find('a:contains(' + self.lang + ')').first();

            $div.addClass('ready');    
            if ($specialLang.length) {
                $specialLang.addClass('special');
                if ($links.length == 1) {
                    return
                }
            }
            $trigger.text($links.length + ' ▾')

            var $dropdown = $('<div class="dropdown dropdown-tip dropdown-anchor-right"/>'),
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
    getTransCounts: function(callback) {
        $.ajax('/data/translation_count?lang=' + sc.intr.lang)
        .done(callback);
    },
    addHasTrans: function() {
        var self = this;
        if (!self.lang) return
        this.getTransCounts(function(data){
            console.log(data);
            var trCounts = data.translation_count;
            $('#panel .contents').each(function(){
                var firstNum = 0;
                $(this).find('a').each(function(){
                    var $a = $(this),
                        href = $a.attr('href'), 
                        uid = href ? href.slice(1) : null;
                    if (uid && trCounts[uid]) {
                        $a.attr('data-translation-count', trCounts[uid]);
                        if (firstNum == 0) {
                            firstNum = trCounts[uid]
                        }
                    } else {
                        $a.attr('data-translation-count', 0);
                    }
                });
                if (firstNum > 0) {
                    var $note = $('<div class="panel-note"/>');
                    $note.append('<a data-translation-count="' + firstNum + '"> </a> ');
                    $note.append(self.lang + ' translations</div>');
                    $(this).append($note);
                }
            });
        });
        
    }   
}

sc.intr.run()
