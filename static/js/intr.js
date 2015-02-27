// Display partially internationalized view

sc.intr = {
    lang: window.localStorage.getItem('sc.intr.lang'),
    run: function() {
        var self = this,
            divtable = $('.divtable');
        var anchors = $($('.tran:contains(' + self.lang + ')').get().reverse());
        //anchors.each(function(i, anchor) {
            ////var parent = $(anchor).parent(),
                ////tr = parent.parent();
            ////parent.prepend(anchor);
            //tr.addClass('has-tran');
        //});

        $('.translations').each(function(i, div){
            $(div).find('a').wrap('<option>');

        }).wrapInner('<select>')

        //anchors.parents('table').find('tr').not('.has-tran').addClass('not-has-tran');
    },
    setLang: function(lang) {
        this.lang = lang;
        window.localStorage.setItem('sc.intr.lang', lang);
        this.run();
    }
}

sc.intr.run()
