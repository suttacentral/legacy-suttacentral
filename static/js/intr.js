// Display partially internationalized view

sc.intr = {
    lang: window.localStorage.getItem('sc.intr.lang') || 'en',
    run: function() {
        var self = this,
            divtable = $('.divtable');
        var anchors = $($('.tran:contains(' + self.lang + ')').get().reverse());

        //anchors.each(function(){
            //$a = $(this);
            //$a.parents('.translations').prepend($a.clone())

        //});

        $('.translations').each(function(){
            var $trans = $(this);
            $a = $trans.find('a:contains(' + self.lang + ')').first()
            if ($a.length) {
                $trans.prepend($a.clone());
            } else {
                $trans.prepend('<span class="tran">  </span>')
            }
        });

        $('.divtable').on('click', '.tran', function(e) {
                self.setLang($(e.target).text())
            });
        

        //anchors.parents('table').find('tr').not('.has-tran').addClass('not-has-tran');
    },
    setLang: function(lang) {
        this.lang = lang;
        window.localStorage.setItem('sc.intr.lang', lang);
    }
}

sc.intr.run()
