sc = window.sc || {};
sc.popup = {
    isPopupHover: false,
    popups: [],
    popup: function(parent, popup, protected) {
        var self = this,
            offset,
            docWith,
            dupe,
            docWidth,
            isAbsolute = false,
            markupTarget = $(document.body);
        if (self.isPopupHover) {
            return false
        }
        
        if (markupTarget.length == 0) {
            markupTarget = $('main');
            if (markupTarget.length == 0) {
                markupTarget = $('body');
            }
        }

        popup = $('<div class="text-popup"/>').append(popup);
        
        function align() {
            popup.removeAttr('style');
            if ('left' in parent || 'top' in parent) {
                offset = parent
                offset.left = offset.left || 0
                offset.top = offset.top || 0
                parent = document.body
                isAbsolute = true

            } else {
                parent = $(parent)
                offset = parent.offset()
            }
            
            //We need to measure the doc width now.
            docWidth = $(document).width()
            // We need to create a dupe to measure it.
            dupe = $(popup).clone()
                
            markupTarget.append(dupe)
            var popupWidth = dupe.innerWidth(),
                popupHeight = dupe.innerHeight();
            dupe.remove()
            //The reason for the duplicity is because if you realize the
            //actual popup and measure that, then any transition effects
            //cause it to zip from it's original position...
            if (!isAbsolute) {
                offset.top += parent.innerHeight() - popupHeight - parent.outerHeight();
                offset.left -= popupWidth / 2;
            }

            if (offset.left < 1) {
                offset.left = 1;
                popup.innerWidth(popupWidth + 5);
            }
            
            if (offset.left + popupWidth + 5 > docWidth)
            {
                offset.left = docWidth - (popupWidth + 5);
            }
            popup.offset(offset)
            markupTarget.append(popup)
            popup.offset(offset)
        }
        
        align();
        popup.data('alignFn', align);
        popup.mouseenter(function(e) {
            self.isPopupHover = true
        });
        function remove() {
            popup.fadeOut(500);
            self.isPopupHover = false

        }
        setTimeout(function(){
            if (!popup.is(':hover')) {
                remove();
            }                
            popup.mouseleave(function(e){
                if (protected) {
                    return
                }
                remove();
            }).mouseenter(function(e){
                self.isPopupHover = true
                popup.stop().fadeIn(0);
            });
        }, 1500)
        this.clear();
        if (protected) {
            popup.data('protected', protected);
        }
        this.popups.push(popup);
        return popup;
    },
    clear: function(clearProtected) {
        var keep = [];
        this.popups.forEach(function(e) {
            if (!clearProtected && e.data('protected')) {
                keep.push(e);
            } else {
                e.remove();
            }
        });
        this.popups = keep;
        this.isPopupHover = false;
        
    }
}
