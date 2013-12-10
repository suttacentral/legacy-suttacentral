""" Functions for converting uids """

import regex

def subdiv_to_div(uid):
    m = regex.match(r'\p{alpha}+(?:-\d+)?', uid)
    return m[0]

def sutta_to_div_subdiv(uid):
    if '.' in uid:
        m = regex.match(r'(\p{alpha}+(?:-\d+)?)(\d*)\.(.*)', uid)
    else:
        m = regex.match(r'(\p{alpha}+(?:-\d+)?)()', uid)
    division = m[1]
    if m[2]:
        subdivision = division + m[2]
    else:
        subdivision = division + '-nosub'
    return (division, subdivision)

def vagga_to_subdiv(vagga_uid):
    return vagga_uid.split('/')[0]