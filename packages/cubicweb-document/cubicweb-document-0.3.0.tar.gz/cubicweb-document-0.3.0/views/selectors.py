from cubicweb.selectors import objectify_selector, Selector

@objectify_selector
def lang_is_defined(cls, req, rset, row=0, col=0, **kwargs):
    doc = rset.get_entity(row, col)
    try:
        doc.lang[0]
        return 1
    except:
        return 0

@objectify_selector
def master_document(cls, req, rset, row=0, col=0, **kwargs):
    doc = rset.get_entity(row, col)
    return 1 if doc.pivot_lang else 0

@objectify_selector
def translatable(cls, req, rset, row=0, col=0, **kwargs):
    untranslated = rset.get_entity(row, col).untranslated_langs
    if len(untranslated):
        return 1
    return 0

@objectify_selector
def is_translation(cls, req, rset, row=0, col=0, **kwargs):
    doc = rset.get_entity(row, col)
    return 0 if doc.pivot_lang else 1

class mimetype(Selector):
    def __init__(self, *mimetypes):
        self.mimetypes = frozenset(mimetypes)

    def __call__(self, cls, req, rset, **kwargs):
        doc = rset.get_entity(0, 0)
        if hasattr(doc, 'branch_head'):
            doc = doc.branch_head()
        if hasattr(doc, 'data_format'):
            format = doc.data_format
        else:
            format = 'application/octet-stream'
        return format in self.mimetypes

@objectify_selector
def not_in_branch_scope(cls, req, rset, row=0, col=0, **kwargs):
    doc = rset.get_entity(row, col)
    if not doc.exists_under_branch_scope():
        return 1
    return 0
