from itertools import chain

class TreeMixin(object):
    # common.mixins.TreeMixIn does not cut it

    # ITree
    def parent(self):
        try:
            return self.filed_under[0]
        except IndexError:
            return None

    def children(self):
        try:
            return self.reverse_filed_under
        except:
            return []

    def is_root(self):
        return self.parent() is None

    def is_leaf(self):
        return True

    def root(self):
        return self.parent().root()

    def iterparents(self):
        par = self.parent()
        if par is None:
            return []
        return chain([par], par.iterparents())
    # /ITree

def _get_branch_scope(req):
    branch = req.form.get('branch')
    if branch is not None:
        return branch
    cookies = req.get_cookie()
    cookiename = 'branch_scope'
    branch_scope = cookies.get(cookiename)
    if branch_scope is None:
        cookies[cookiename] = branch = u'default'
        req.set_cookie(cookies, cookiename)
    else:
        branch = branch_scope.value
    return branch
