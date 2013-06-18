#!/usr/bin/env python3.3
import domunator; from domunator import *

numRex = regex.compile(r'\s*(?P<num1>[0-9]+)(?:–​)?(?P<num2>[0-9]+)?\.?\s*(?P<text>.*)')

#Apply any regular expressions to the document as a text string
def applyRexes(doc, filename):
    doc = regex.sub('\n\s*', ' ', doc) #Remove all newlines and trailing whitespace
    doc = doc.translate(str.maketrans('ṁṀ', 'ṃṂ'))
    return doc

#Make modifications to the Document Model
def process(dom, filename):
    try:               selectOne('#onecol').set('id', 'text')
    except IndexError: pass

    if not exists('#metaarea'):
        dom.body.append(create("div", id="metaarea"))
    metaarea = selectOne('#metaarea')
    metaarea.append(create("<p>" + "Pali text from the Mahāsaṅgīti Tipiṭaka Buddhavasse 2500: World Tipiṭaka Edition in Roman Script. Edited and published by The M.L. Maniratana Bunnag Dhamma Society Fund, 2005. Based on the digital edition of the Chaṭṭha Saṅgāyana published by the Vipassana Research Institute, with corrections and proofreading by the Dhamma Society." + "</p>"))

    for element in select('div.hidden'):
        metaarea.append(element) #Note: An element is always moved, never copied! :)

    #Remove all existing hgroups
    for hgroup in select('hgroup'):
        unwrap(hgroup)

    hgroupHeadings()

    for hgroup in select('hgroup'):
        if len(hgroup) > 1:
            if ( hgroup[0].tag, hgroup[1].tag ) == ( 'h3', 'h2' ):
                hgroup[0].tag, hgroup[1].tag = ('h2', 'h3')

    for a in select('a.pts, a.wp, a.ms, a.msdiv, a.sc, a.vnS, a.vn, a.vimula, a.tu, a.gatn, a.t, a.tlinehead, a.bb'):
        a.text = None

    for a in select('[lang=pi]'): del(a.attrib['lang'])
    selectOne("#text").attrib["lang"] = 'pi'

    collection, suffix = regex.match(r'(?:.*/)?([[:alpha:]]+)([0-9.-]+)[^/]*$', filename)[1:]


    if collection in ['dhp']:
        specialDHP()

    if collection in ['snp', 'ud', 'it']:
        specialKhn()
    if collection in ['snp']:
        specialSNP(collection, suffix)
    if collection in ['ud']:
        specialUd(collection, suffix)
    if collection in ['it']:
        specialIt()


    if collection in ['dn', 'mn']:
        specialMNandDN()
    else:
        specialOther()

    for summary in select('p.summary'):
        pclass = "uddanagatha"
        text = summary.text_content()
        if 'vagg' in text:
            pclass = "vagguddanagatha"
        nextelement = summary.getnext()
        if nextelement.tag == 'blockquote':
            nextelement.set('class', pclass)

    conformsections()
    h1s = select('h1 > a')
    if len(h1s) > 1:
        for h in h1s:
            m = numRex.match(h.text)
            ref = m["num1"]
            if m["num2"] != None:
                ref += "-" + m["num2"]
            for i in h.iterancestors():
                if i.tag == 'section':
                    i.set('id', ref)
                    break
    #Attach the toc to the wrapping div
    selectOne('#text').insert(0, selectOne('#toc'))
    log()

    #Add newlines back in.
    newlineify()
    return dom

def specialKhn():
    for h in select('h3'): h.tag = 'h2'
    for h in select('h1'):
        m = numRex.match(h.text)
        h.text = m["text"]
    for a in select('span.brnum'):
        num = regex.search(r'[0-9]+', a.text)[0]
        parent = a.getparent()
        destroy(a)
        parent.insert(0, create('<a class="brnum" id="br{}"></a>'.format(num)))

def specialIt():
    for a in select('a.msdiv'):
        destroy(a)

def specialUd(collection, suffix):
    udNum = Adder(1,1)

    prefix = collection + suffix
    for a in select('a.sc'):
        a.set('id', '{}{}'.format(prefix, udNum()))
    for h in select('hgroup'):
        try            : del(h.attrib['id'])
        except KeyError: pass

snpVerseNum = Adder(1, 1)
def specialSNP(collection, suffix):
    for a in select('a.sc, a.gatn'):
        destroy(a)
    for a in select('a.msdiv'):
        parent = a.getparent()
        destroy(a)
        parent.insert(0, create('<a class="sc" id="sc{}"></a>'.format(snpVerseNum())))
    for p in select('blockquote.gatha > p'):
        for child in p.iterchildren():
            if child.tail != None:
                m = regex.match(r'(.*)(\([^(]+\))(.*)', child.tail)
                if m:
                    pre, speaker, post = m[1:]
                    child.tail = pre + post
                    p.addprevious(create('<span class="speaker">{}—</span>'.format(speaker)))
                    break
    for h in select('hgroup'):
        try            : del(h.attrib['id'])
        except KeyError: pass

def specialDHP():
    filenameRex = regex.compile(r'(?:.*/)(?P<uid>[[:alpha:]]+)(?P<num1>[0-9]+)-?(?P<num2>[0-9]+)?')
    h1s = select('h1')
    h2s = select('h2')
    h3s = select('h3')
    for h in h1s: h.tag = 'h3'
    for h in h2s: h.tag = 'h1'
    for h in h3s: h.tag = 'h2'

    for hgroup in select('hgroup'): unwrap(hgroup)
    hgroupHeadings()

    for h in select('h3'): h.text = numRex.sub('\g<text>', h.text)
    for h in select('h2 > a'): h.text += '.'

    def renumber(start, end, uid):
        suttaNum = start - 1
        pNum = 0
        for i in select("#text, body")[-1].iter():
            if (i.tag == 'h1'):
                suttaNum += 1
                pNum = 0
                proxy = i.getchildren()[0]
                m = numRex.match(proxy.text)
                if m["num2"] == None:
                    suttaNumText = str(suttaNum) + '.'
                    suttaNumRef = suttaNumText
                else:
                    width = int(m["num2"]) - int(m["num1"])
                    suttaNumText = "{}–​{}.".format(suttaNum, suttaNum + width)
                    suttaNumRef = "{}-{}.".format(suttaNum, suttaNum + width)
                    suttaNum += width
                proxy.text = suttaNumText + m.expand(r" \g<text>")
            elif i.tag == 'a' and 'class' in i.attrib and i.get("class") == 'sc':
                pNum += 1
                i.set('id', "{}{}{}".format(uid, suttaNumRef, pNum))
    m = filenameRex.match(domunator.filename)
    renumber(int(m["num1"]), int(m["num2"]), m["uid"])

def specialOther():
    for element in select('article'): unwrap(element)

    for hgroup in select('hgroup'):
        article = wrap(hgroup, 'article')
        for i in article.itersiblings():
            if i.tag == 'hgroup': break
            article.append(i)
    pass

def specialMNandDN():
    h1 = selectOne('h1')
    h2 = h1.getprevious()
    if h2.tag == 'h2':
        m = regex.match(r'\s*([0-9]+)\.?\s*(.*)', h1.text)
        h1.text = m[2]
        h2.text = h2.text + '\xa0' + m[1]
    for s in select('section'):
        unwrap(s)
    for a in select('article.sutta'):
        wrap(a, 'section', attribtheft = True)
    for a in select('.chapter'):
        del(a.attrib['class'])
        a.attrib['id'] = 'chapter'

processFiles(applyRexes, process)