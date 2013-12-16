#!/usr/bin/env python

def csx2utf(bytes):
    """Convert a byte string encoded in csx+, into a unicode string
    
    Works both on properly encoded csx+, and also utf8 resulting
    from a tool treating csx+ as latin1 (for example a word processor
    might export a csx+ document to HTML using utf8 encoding, with no option
    to change the encoding). The case is auto-detected.
    
    """
    # There are two modes: First you might get a file which has been
    # mistakenly converted to utf8 by a program assuming latin1. Or secondly
    # you might have a file properly encoded as csx+, in which case we'll
    # deliberately convert it to utf8 as if it were latin1 and proceed as if 
    # it had been wrong to begin with. Anyone with more obscure problems can
    # modify the source ;).

    try:
        string = bytes.decode('utf8')
    except UnicodeDecodeError:
        string = bytes.decode('latin1')
    return string.translate(str.maketrans(
                      'àâãäåæ\x83\x88\x8c\x93\x96çèéêëìíîïð¤¥ñòóôõö÷øùú§üýþÿ',
                      'āĀīĪūŪâêîôûṛṚṝṜḷḶḹḸṅṄñÑṭṬḍḌṇṆśŚṣṢṁṃṂḥḤ'))

if __name__=='__main__':
    import sys
    try:
        infile = sys.argv[1]
        outfile = sys.argv[2]
        with open(infile, 'rb') as f:
            bytes = infile.read()
        with open(outfile, 'w', encoding='utf8') as f:
            f.write(csx2utf(bytes))
    except IndexError:
        print('Usage: csx2utf infile outfile')
        
    
    