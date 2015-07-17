sc.epigraph = {
    max: +$('.epigraph').attr('data-num-epigraphs'),
    reset: function(){
        this.remains = [];
        for (var i = 0; i < this.max; i++) {
            this.remains.push(i);
        }
    },
    init: function(){
        var self = this;
        if ($('#home').length == 0) return
        self.reset();
        self.loadRandom();
        $('.epigraph > a').click(function(){
            var num = +$('.epigraph-text').attr('data-num');

            if ($(this).hasClass('next')) {
                num += 1;
            } else if ($(this).hasClass('previous')) {
                num -= 1;
            } else if ($(this).hasClass('num')) {
                self.loadRandom();
                return
            }
            num = (num + self.max) % self.max;
            self.loadEpigraph(num);
        })
    },
    loadEpigraph: function(num) {
        jQuery.ajax('/epigraphs/' + num, {cache: true})
            .done(function(data, status, xhr) {
                var existing = $('.epigraph > div');
                if (existing.length) {
                    existing.fadeOut(function(){
                        $(data).replaceAll(existing).hide().fadeIn();
                    })
                } else {
                    $('.epigraph > div').replaceWith(data)
                }
                $('.epigraph > .num').text(+num + 1);
            });
    },
    loadRandom: function(){
       var current = $('.epigraph-text').attr('data-num') || -1,
            index,
            num;
        if (this.max <= 0) return
        if (this.remains.length == 0) this.reset()

        index = Math.floor(Math.random() * this.remains.length)
        // Used this way (i.e. with nothing to insert)
        // splice returns the element at index
        // and removes that element from the array.
        num = this.remains.splice(index, 1);
        console.log('Loading one at {}'.format(num))
        this.loadEpigraph(num);
    }
}
sc.epigraph.init();

