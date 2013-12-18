""" Analyzes the Sutta Central text repository

Produces statistics on tags, classes and their usage.

This can be used for validation of incoming texts.

The json output is designed to be diff-friendly.

"""

import pathlib, collections, json
import lhtmlx
import config

def analyze_path(path):
    by_tag = collections.defaultdict(collections.Counter)
    by_class = collections.defaultdict(collections.Counter)
    pnum_classes = {}
    for infile in path.glob('**/*.html'):
        doc = lhtmlx.parse(str(infile), encoding='utf8')
        for e in doc.getroot().cssselect('[class]'):
            for class_ in e.attrib['class'].split():
                by_tag[e.tag][class_] += 1
                by_class[class_][e.tag] += 1
                if 'id' in e.attrib and not e.text_content():
                    by_class[class_]['pnum'] += 1
                    
    
    defaults = {}
    for class_, counter in by_class.items():
        pnum_count = counter['pnum']
        if pnum_count:
            del counter['pnum']
        tag, count = counter.most_common(1)[0]
        defaults[class_] = tag
        if pnum_count > count / 2:
            pnum_classes[class_] = pnum_count
    
    return {'defaults': defaults, 
            'by_tag': {tag: dict(val) for tag, val in by_tag.items()},
            'by_class': {class_: dict(val) for class_, val in by_class.items()},
            'pnum_classes': pnum_classes}

data_file_json = pathlib.Path(config.base_dir) / 'utility' / 'tag_data.json'

def save_sc_class_data():
    tag_class_data = analyze_path(pathlib.Path(config.text_dir))
    json.dump(tag_class_data, data_file_json.open('w'), indent=4, sort_keys=1)

def load_sc_class_data():
    jdata = json.load(data_file_json.open('r'))

def test():
    test = """
import imp
import pathlib, env, config
import htmlproc.analysis
htmlproc.analysis.save_sc_class_data()
htmlproc.analysis.load_sc_class_data()

by_class = htmlproc.analysis.analyze_path(pathlib.Path(config.text_dir))
    """
