/* The notes module is responsible for generating the dynamic
 * variant and cross reference notes.
 */

sc.notes = {
    sourceAttr: 'title', // We could also use a data- attribute
    init: function(){
        $('#text').on('mouseover', '.var, .cross', sc.notes.markupNote);
        

    },
    markupNote: function(event){
        "use strict";
        if ($(event.target).find('.deets').length) return;
        var self=sc.notes,
            $e = $(event.target),
            note_obj = $.parseJSON($e.attr(self.sourceAttr));
        if ($e.is('.var')) {
            $e.append(self.markupVarNote(note_obj));
        } else if ($e.is('.cross')) {
            $e.append(self.markupXRefNote(note_obj));
        }
    },
    markupVarNote: function(note_obj) {
        var self = this,
            table = $('<table class="deets">'),
            note,
            row,
            td,
            i;
        //$(e).removeAttr(self.sourceAttr)
        /* The note object at the top level is an array */
        for (i = 0; i < note_obj.length; i++) {
            note = note_obj[i];
            /* We use Duck Typing */
            row = $('<tr>').appendTo(table);
            if ('var' in note){
                /* We should have two columns */
                row.append($('<td>').text(note['var']))
                /*  Now we need to make sense of the note itself */
                td = $('<td>').appendTo(row);
                if ('eds' in note) {
                    td.html('<ul>' + note['eds'].map(function(ed){
                        return '<li>' + sc.util.expand_uid_data[ed][1];
                    }).join('\n') + '</ul></td>')
                }
                if ('note' in note) {
                    td.append(note['note']);
                }
            }
        }
        return table;
    },
    markupXRefNote: function(note_obj){
        var self=this,
            note,
            ul = $('<ul class="deets">'),
            li,
            i;

        for (i = 0; i < note_obj.length; i++) {
            note = note_obj[i];
            li = $('<li>').appendTo(ul);
            if (note.from) {
                li.append(self.xRefToHTML(note.from));
                li.append('–');
                li.append(self.xRefToHTML(note.to));
            } else {
                li.append(self.xRefToHTML(note));
            }
        }

        return ul;
    },
    xRefToHTML: function(obj){
        /* A XRef has these attributes:
         * lang - The Language Code (uid, path component)
         * uid  - The sutta uid
         * bm   - Bookmark on the page
         * desc - A description of the page (normally the heading)
         */

        var title,
            href,
            out = $('<a class="xref">');

        href = obj.lang ? '../{}/'.format(obj.lang) : './';
        
        href += obj.uid
        if (obj.bm) {
            href += '#' + obj.bm;
        }
        
        out.attr('href', href)
        title = sc.util.uidToAcro(obj.uid)
        if (obj.bm) {
            title += '.' + obj.bm;
        }
        if (obj.desc) {
            title += ' ' + obj.desc.replace(/^[\d–.\u2060]*\s*/, '');
        }
        out.text(title);
        return out
    },
}

$(document).ready(sc.notes.init);
