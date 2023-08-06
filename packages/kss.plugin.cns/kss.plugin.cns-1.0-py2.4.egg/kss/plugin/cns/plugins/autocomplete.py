# A function to create esacped vocab from DisplayList for autocomplete plugin

def autocomplete_escape(disp_list):
    esc_vocab = [v.replace(u'\'', u'\\\'') for v in disp_list.values()]
    return u'\'' + u'\',\''.join(esc_vocab) + u'\''