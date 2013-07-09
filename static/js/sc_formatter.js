//Shims
if (String.prototype.trimLeft === undefined)
{
    String.prototype.trimLeft = function() {
        return this.replace(/^\s+/,"");
    }
}

sc_formatter = {
    //Designed to workaround limitations in css.
    init: function() {//Init is called only once.
        //$("body").on("mouseover", "span.lookup", function(e){sc_formatter.rePosition($(e.target))})
        $(window).resize(function(){
            //sc_formatter.shove();
            
            //$("span.lookup").mouseenter(function(e){sc_formatter.rePosition($(e.target))});
        });
        $(document).on('keydown', sc_formatter.deathToTheBeast);
        this.apply();
        this.operaFix();
    },
    apply: function(){
        $("tr").filter(":even").addClass("even"); //Add the .even class to every second tr element
        //$(".altVolPage").attr("title", scMode[scMode.lang].strings["altVolPage"]);
        //$(".altAcronym").attr("title", scMode[scMode.lang].strings["altAcronym"]);
        sc_formatter.quoteHanger();
        
    },
    shove: function(){
        var start = (new Date()).getTime();
        $("q").each(function(){sc_formatter.rePosition($(this))});
        //console.log("Resize took: ", (new Date()).getTime() - start, " milliseconds");
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
    operaFix: function(){
        if ('opera' in window) {
            if ('version' in window.opera && window.opera.version > 12.2)
            {
                return;
            }
            $(document.body).addClass('badfonts');
        }
    },
    quoteHanger: function(){
        $('p').each(function(){
            children = this.childNodes
            for (i=0; i < children.length; i++)
            {
                child = children[i]
                if (child.nodeType == 3)
                {
                    text = child.nodeValue.trimLeft()
                    var firstChar = text[0];
                    if (firstChar == '“' || firstChar == '‘')
                    {
                        var secondChar = text[1];
                        if (secondChar == '“' || secondChar == '‘')
                        {
                            child.nodeValue = text.slice(2);
                            $(this).prepend('<span class="dsquo">' + firstChar + secondChar + '</span>');
                        } else {
                            child.nodeValue = text.slice(1);
                            if (firstChar == '‘') {
                                $(this).prepend('<span class="squo">' + firstChar + '</span>');
                            } else {
                                $(this).prepend('<span class="dquo">' + firstChar + '</span>');
                            }
                        }
                    }
                    break
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
                    if (sc_formatter.markOfTheBeast % 2 == 0) {
                        node.nodeValue = node.nodeValue.replace(/ṃ/g, 'ṁ').replace(/Ṃ/g, 'Ṁ');
                    } else {
                        node.nodeValue = node.nodeValue.replace(/ṁ/g, 'ṃ').replace(/Ṁ/g, 'Ṃ');
                    }
                }
            }
            textualControls.enable();
            if (sc_formatter.markOfTheBeast % 2 == 0) {
                //console.log("It took " + (Date.now() - startTime) + "ms but the world is safe once again.");
            } else {
                var num = 1 + Math.ceil(sc_formatter.markOfTheBeast / 2);
                var suffix = 'th';
                if (num % 10 == 1 && num % 100 != 11) suffix = 'st';
                if (num % 10 == 2 && num % 100 != 12) suffix = 'nd';
                if (num % 10 == 3 && num % 100 != 13) suffix = 'rd';
                //console.log("For the "+ num + suffix + " time the world is plunged into darkness.");
            }
            sc_formatter.markOfTheBeast += 1
        }
    }
}
sc_formatter.init();