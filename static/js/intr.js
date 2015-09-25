// Display partially internationalized view

sc.intr = {
    lang: window.localStorage.getItem('sc.intr.lang') || 'en',
    run: function() {
        var self = sc.intr;
        if ($('#home').length == 0) {
            $('.translations').each(function(i, div){
            
                var $div = $(div),
                    id = "dropdown-" + (i + 1),
                    $links = $div.find('.tran'),
                    $trigger = $('<a href="#"/>'),
                    $specialLang = $div.find('a:contains(' + self.lang + ')').first();
                if ($links.length == 0) return
                $div.addClass('ready');    
                if ($specialLang.length) {
                    $specialLang.addClass('special');
                    $div.prepend($specialLang);
                    if ($links.length == 1) {
                        
                        return
                    }
                }
                $trigger.text($links.length - 1 + ' ▾')

                var $dropdown = $('<div class="dropdown dropdown-relative dropdown-tip dropdown-anchor-right"/>').hide(),
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
            console.log('Hiding dropdowns');
        }

        $('.divtable').on('click', '.tran', function(e) {
                self.setLang($(e.target).text())
            });
        self.addHasTrans();
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
        $.ajax('/data?translation_count=&langs=&lang=' + sc.intr.lang)
        .done(callback);
    },
    makeLangSwitcher: function(langs){
        var out = $('<span class="switcher"/>');
        for (key in langs) {
            if (!langs[key].root) {
                out.append('<a class="lang-switch" href="#' + key + '">' + key + '</a>');
            }
        }
        return out
    },
    addHasTrans: function() {
        var self = sc.intr;

        this.getTransCounts(function(data){
            self.trCounts = data.translation_count;
            self.langs = data.langs;
            self.addLangNames();
            if (!self.lang) return

            var polyglot = new Polyglot({phrases: self.data[self.lang],
                                        locale: self.lang}),
                        t = polyglot.t.bind(polyglot);
        
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
                        $a.attr('title', t("n_translations", self.trCounts[uid]));
                    }
                });
            });
        });
        $('#panel').on('click', '.lang-switch', self.switchLang);
    },
    addLangNames: function(){
        $('.translations .tran:not(.special)').each(function(i, tran) {
            var uid = $(tran).text();
            $(tran).attr('data-name', sc.intr.langs[uid].name);
        });
    },
    data: {
        // Pluralization Group 'Chinese' (one) 1/plural
        id: {
            n_translations: "%{smart_count} terjemahan dalam bahasa Indonesia"
        },
        zh: {
            n_translations: "%{smart_count}翻譯在汉语"
        },
        th: {
            n_translations: "%{smart_count} การแปล เป็นภาษาไทย"
        },
        vi: {
            n_translations: "%{smart_count} bản dịch bằng tiếng Việt"
        },
        // Pluralization Group 'German' (two)
        en: {
            n_translations: "%{smart_count} translation in english||||%{smart_count} translations in english"
        },
        no: {
            n_translations: "%{smart_count} En oversettelse i norsk||||%{smart_count} oversettelser i norske"
        },
        sv: {
            n_translations: "%{smart_count} översättningen på svenska||||%{smart_count} översättningar i svenska"
        },
        ca: {
            n_translations: "%{smart_count}  traducció en català||||%{smart_count} traduccions en català"
        },
        nl: {
            n_translations: "%{smart_count} 1 vertaling in het Nederlands||||%{smart_count} vertalingen in het Nederlands"
        },
        de: {
            n_translations: "%{smart_count} Übersetzung in Deutsch||||%{smart_count} Übersetzungen in Deutsch"
        },
        hi: {
            n_translations: "हिन्दी में एक अनुवाद||||हिन्दी में %{smart_count} में अनुवाद"
        },
        hu: {
            n_translations: "%{smart_count} fordítását magyarul||||%{smart_count} fordításokat Magyar"
        },
        it: {
            n_translations: "%{smart_count} traduzione in italiano||||%{smart_count} traduzioni in italiano"
        },
        pt: {
            n_translations: "%{smart_count} tradução em Português||||%{smart_count} traduções em português"
        },
        es: {
            n_translations: "%{smart_count} traducción en español||||%{smart_count} traducciones en español"
        },
        si: {
            n_translations: "සිංහල %{smart_count} පරිවර්තනය||||සිංහල %{smart_count} පරිවර්තන"
        },
        //Pluralization Group 'French' (three) 0/plural
        fr: {
            n_translations: "%{smart_count} traductions en français||||%{smart_count} traductions en français"
        },
        my: {
            n_translations: "ဗမာထဲတွင် 0 င် ဘာသာပြန်||ဗမာထဲတွင် 23 ဘာသာပြန်ချက်များကို"
        },
        ko: {
            n_translations: "%{smart_count} 한국어 0 번역||||한국어 %{smart_count} 번역"
        },
        //Pluralization Group 'Russian' (four)
        ru: {
            n_translations: "%{smart_count} переводом на русский язык||||%{smart_count} переводах на русский||||%{smart_count} Перевод на русском языке"
        },
        //Pluralization Group 'Czech' (five)
        cs: {
            n_translations: "%{smart_count} překlad do češtiny||||%{smart_count} překlady v češtině||||%{smart_count} překlady v češtině"
        },
        //Pluralization Group 'Polish' (six)
        pl: {
            n_translations: "%{smart_count} Tłumaczenie w języku polskim||||%{smart_count} tłumaczenia w języku polskim||||%{smart_count} tłumaczeń w języku polskim"
        }
    }
}
sc.intr.run()
