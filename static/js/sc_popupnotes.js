/* The notes module is responsible for generating the dynamic
 * variant and cross reference notes.
 */

sc.notes = {
    /* This is the documentation for the variant notes used on
     * sutta central. The content of a note, stored in the title tag
     * is human-readable (as a title), it is in fact based very closely
     * on the original MS notes. The notes have been massaged slightly
     * so they are more consistent and so they are more machine-readable.
     */
    
    // Rows are split by a spaced vertical bar. In the original, they
    // were comma seperated. Rows here are basically distinct 'things'.
    rowRex: / \| /,

    // A 'note' can be properly split into a variant reading and a comment
    // The variant reading is defined as either a bracketed segment of
    // text (the rare case, for representing texts in brackets in the root)
    // or everything before the bracketed edition names.
    // However in some cases notes are pure notes and have no variant reading.
    varRex: /^(\(.*?\)|[^\(]+)(.*)/,

    // Editions are matched literally (as words) anywhere in a note
    edsRex: self.edsRex,

    // Round brackets (when not used for a variant reading) normally
    // contain a comma seperated list of editions.
    robrContentsRex: /\((.*?)\)([^\)]*)/g,
    
    // A cross reference starts with a hat, is followed by a url
    // component and then, in square brackets, a title. Finally,
    // there can be a comment. Cross references can occur
    // both in cross tags, and in var tags. When they are in var tags
    // they normally mean 'see usage/form here'.
    xrefRex: /\^([\w.\-]+(?:#\w+)?)\s*(?:\[(.*?)\])?(.*)/g,
    
    sourceAttr: 'title', // We could also use a data- attribute
    init: function(){
        $('#text').on('mouseover', '.var, .cross', sc.notes.markupNote);
        

    },
    markupNote: function(event){
        "use strict";
        var self = sc.notes;
        if ($(event.target).find('.deets').length) return;
        var $target = $(event.target),
            noteData = $target.attr(self.sourceAttr);
        if ($target.is('.var')) {
            $target.append(self.markupVarNote(noteData));
        } else if ($target.is('.cross')) {
            $target.append(self.markupXRefNote(noteData));
        }
        $target.attr(self.sourceAttr, null);
    },
    markupVarNote: function(noteData) {
        var self = this;
        
        return $('<table class="deets">').append(
            noteData.split(self.rowRex).map(
                function process_row(row_text) {
                var m = row_text.match(self.varRex),
                    variant = m[1],
                    comment = m[2],
                    out;
                if (variant && !comment) {
                    // In some cases there is no variant, it's simply a comment
                    // In this case, the comment takes the entire line.
                    out = '<tr><td colspan=2>{}</td></tr>'.format(self.markupComment(variant));
                } else {
                    // The normal case is a variant and a comment or qualification
                    // pertaining to that variant reading.
                    out = '<tr><td>{}</td><td>{}</td>'.format(variant, self.markupComment(comment));
                }
                return $(out);
            })
        );
    },
    markupXRefNote: function(comment){
        var self=this,
            note;
        rows = comment.split(self.rowRex).map(function(row){
            var markedRow = row.replace(self.xrefRex, self.xRefToHTML);
            if (markedRow == row) {
                markedRow = '<td colspan=2>' + row + '</td>'
            }
            return '<tr>' + markedRow + '</tr>';
        })

        return '<table class="deets">' + rows.join('\n') + '</table>'
        return ul;
    },
    markupComment: function(comment){
        var self = this;
        comment = comment.replace(self.robrContentsRex, function(m, contents, leftovers){
            if (contents) {
                contents = '<ul>' + contents.split(/,\s*/g).map(function(part){
                    part = part.replace(self.edsRex, function(ed){
                        var res = self.editionsExpansionData[ed];
                        if (!res){ed}
                        return res[1];
                    });
                    return '<li>' + part + '</li>';
                }).join('\n') + '</ul>';
            }
            return contents + leftovers;
        });
        return comment
        

    },
    xRefToHTML: function(m, urlComp, title, desc){
        /* A XRef has these attributes:
         * lang - The Language Code (uid, path component)
         * uid  - The sutta uid
         * bm   - Bookmark on the page
         * desc - A description of the page (normally the heading)
         */
        var parts = urlComp.split('#'),
            uid = parts[0],
            bm = (parts.length > 1) ? parts[1] : null,
            href = './' + uid + (bm ? '#' + bm : ''),
            acro = sc.util.uidToAcro(uid);
        
            if (desc) {
                title = desc.replace(/^[\d–.\u2060]*\s*/, '');
            }

        return '<td><a class="xref" href="{}">{}</a></td><td>{}</td>'.format(href, acro, title)
    },
    editionsExpansionData: {
        'sī1': ["Bj", "Buddhajayantītripiṭakagranthamālā 2501–2531 (1957–1989)"],
        'c-a': ["C-A", "Chaṭṭhasaṅgīti Piṭakaṃ Atthakathā"],
        'c1': ["C1", "Chaṭṭhasaṅgīti Piṭakaṃ 2496–2499 (1952–1955)"],
        'c2': ["C2", "Chaṭṭhasaṅgīti Piṭakaṃ 2nd ed. 2500–2506 (1956–1962)"],
        'c3': ["C3", "Chaṭṭhasaṅgīti Piṭakaṃ (1997)"],
        'cha1': ["C1", "Chaṭṭhasaṅgīti Piṭakaṃ 2496–2499 (1952–1955)"],
        'cha2': ["C2", "Chaṭṭhasaṅgīti Piṭakaṃ 2nd ed. 2500–2506 (1956–1962)"],
        'cha3': ["C3", "Chaṭṭhasaṅgīti Piṭakaṃ (1997)"],
        'mr': ["Mr", "Maramma Tipiṭaka 2541 (1997)"],
        'ka-ma': ["Mr", "Maramma Tipiṭaka 2541 (1997)"],
        'si': ["Si", "Sinhala Tipiṭaka 2501 (1957)"],
        'ka-sī': ["Si", "Sinhala Tipiṭaka 2501 (1957)"],
        'km': ["Km", "Phratraipiṭakapāḷi 2501–2512 (1958–1969)"],
        'maku': [" Maku", "Mahāmakurājāvidyālai 2466 (1923)"],
        'pts-a': ["PTS-A", "Pali Text Society Atthakathā"],
        'pts1': ["PTS 1", "Pali Text Society 1st ed. 2424–2535 (1881–1992)"],
        'pts2': ["PTS 2", "Pali Text Society 2nd ed. 2517–2541 (1974–1998)"],
        'pā1': ["PTS 1", "Pali Text Society 1st ed. 2424–2535 (1881–1992)"],
        'pā2': ["PTS 2", "Pali Text Society 2nd ed. 2517–2541 (1974–1998)"],
        's-a': ["S-A", "Syāmaraṭṭhassa Tepiṭakaṃ Atthakathā"],
        's1': ["S 1", "Chulachomklao Pāḷi Tipiṭaka 2436 (1893)"],
        's2': ["S 2", "Syāmaraṭṭhassa Tepiṭakaṃ 2469–2471 (1926–1928)"],
        's3': ["S 3", "Syāmaraṭṭhassa Tepiṭakaṃ 2538 (1995)"],
        'syā1-3': ["S 1-3", "Chulachomklao Pāḷi Tipiṭaka 2436 (1893), Syāmaraṭṭhassa Tepiṭakaṃ 2469–2471 (1926–1928) & 2538 (1995)"], 
        'syā1': ["S 1", "Chulachomklao Pāḷi Tipiṭaka 2436 (1893)"],
        'syā2': ["S 2", "Syāmaraṭṭhassa Tepiṭakaṃ 2469–2471 (1926–1928)"],
        'syā3': ["S 3", "Syāmaraṭṭhassa Tepiṭakaṃ 2538 (1995)"], 
        'bj': ["Bj", "Buddhajayantītripiṭakagranthamālā 2501–2531 (1957–1989)"],
        'bj-a': [" Bj A", "Buddhajayantītripiṭakagranthamālā Atthakathā)"]
    },
}

sc.notes.edsRex = (function(){
    var edUids = [];
    for (uid in sc.notes.editionsExpansionData) {
        edUids.push(uid);
    }
    edUids.sort(function(e){return e.length});
    return RegExp('\\b({})\\b'.format(edUids.join('|')), 'g');
})()


$(document).ready(sc.notes.init);
