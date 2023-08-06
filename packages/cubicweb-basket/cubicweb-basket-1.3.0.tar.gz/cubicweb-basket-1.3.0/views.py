"""Specific views for baskets

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb import Unauthorized
from cubicweb.selectors import implements
from cubicweb.web import uicfg, box, action
from cubicweb.web.htmlwidgets import BoxWidget
from cubicweb.web.views import primary

# displayed by the basket box
uicfg.primaryview_section.tag_subject_of(('*', 'in_basket', '*'), 'hidden')
uicfg.primaryview_section.tag_object_of(('*', 'in_basket', '*'), 'hidden')


class BasketPrimaryView(primary.PrimaryView):
    __select__ = implements('Basket',)
    entity_name = 'Basket'
    nothing_msg = _('nothing in basket')
    content_msg = _('items in this basket')

    def display_title(self, entity):
        self.w(u"<span class='title'><b>%s : %s</b></span>" % (
            self._cw._(self.entity_name), xml_escape(entity.name)))

    def display_content(self, entity):
        rset = self._cw.execute('Any I WHERE I in_basket B,  B eid %(x)s',
                                {'x': entity.eid}, 'x')
        self.w('<h5>%s</h5>' % self._cw._(self.content_msg))
        if rset:
            self.wview('list', rset)
        else:
            self.w(self._cw._(self.nothing_msg))

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'&nbsp;')
        self.display_title(entity)
        if entity.description:
            self.w(u'<div class="contentBox">%s</div>' %
                   entity.printable_value('description'))
        self.display_content(entity)

def insert_eids(actions, eids):
    """ insert into the __linkto values of actions all the eids
        this processing also filters out all the actions which don't have a linkto action
    """
    processed_actions = []
    for action_id, action_label, action_dict in actions:
        if isinstance(action_dict, str):
            continue
        if action_dict.get('__linkto', None):
            r_type, old_eids, target = action_dict['__linkto'].split(':')
            action_dict['__linkto'] = '%s:%s:%s' % (r_type,
                                                    '_'.join([str(x) for x in eids]),
                                                    target)
            processed_actions.append((action_id, action_label, action_dict))
    return processed_actions



class BasketBox(box.UserRQLBoxTemplate):
    """display a box containing all user's basketitems"""
    __regid__ = 'basket_box'
    visible = False # disabled by default
    order = 30
    title = _('basket')
    rql = 'Any B,N where B is Basket,B owned_by U, U eid %(x)s, B name N'
    etype = 'Basket'
    rtype = 'in_basket'


    def selected_eids(self):
        selectedeids = ()
        if self.cw_rset:
            # something is being displayed. If the first column contains eids,
            # fetch them so we can propose to add the selection to the basket
            etype = iter(self.cw_rset.column_types(0)).next()
            if not self._cw.vreg.schema.eschema(etype).final:
                selectedeids = set(row[0] for row in self.cw_rset.rows)
        return selectedeids

    def build_inbasket_link(self, box, basket):
        rset = basket.related('in_basket', 'object')
        title = u'%s <span class="basketName">%s</span> (%s)' % (
            _('view basket'), xml_escape(basket.name), len(rset))
        box.append(self.mk_action(title, basket.absolute_url(),
                                  escape=False))
        return rset, [row[0] for row in rset]

    def build_add_link(self, box, basket, addable, rql, vid):
        title = u'%s <span class="basketName">%s</span>' % (
            _('add to basket'), xml_escape(basket.name))
        linkto = u'in_basket:%s:object' % '_'.join(addable)
        msg =  _('selection added to basket')
        url = self._cw.build_url('edit', eid=basket.eid, rql=rql,
                                 __linkto=linkto, __message=msg,
                                 __redirectrql=rql, __redirect_vid=vid)
        box.append(self.mk_action(title, url, category='manage',
                                  escape=False))

    def build_delete_link(self, box, basket, inbasketeids, rql, vid):
        title = '%s <span class="basketName">%s</span>' % (
            _('reset basket'), xml_escape(basket.name))
        delete = '%s:in_basket:%s' % ('_'.join(str(eid) for eid in inbasketeids),
                                      basket.eid)
        msg =  _('Basket %s emptied') % basket.name
        url = self._cw.build_url('edit', rql=rql, __delete=delete,
                                 __message=msg, __redirectrql=rql,
                                 __redirect_vid=vid)
        box.append(self.mk_action(title, url, category='manage'))

    def call(self, **kwargs):
        try:
            baskets = self._cw.execute(*self.to_display_rql())
        except Unauthorized:
            # can't access to something in the query, forget this box
            return
        _ = self._cw._
        req = self._cw
        box = BoxWidget(_(self.title), self.__regid__)
        rschema = self._cw.vreg.schema.rschema(self.rtype)
        actions = []
        rql = req.form.get('rql') or kwargs.get('rql') or ''
        vid = req.form.get('vid', '')
        selectedeids = self.selected_eids()
        itemsrql = 'Any X WHERE X in_basket B, B eid %(x)s'
        for basket in baskets.entities():
            rset, inbasketeids = self.build_inbasket_link(box, basket)
            if selectedeids and rschema.has_perm(req, 'add'):
                addable = [str(eid) for eid in selectedeids if not eid in inbasketeids]
                if addable:
                    self.build_add_link(box, basket, addable, rql, vid)
            if not rset:
                continue
            if rschema.has_perm(req, 'delete'):
                self.build_delete_link(box, basket, inbasketeids, rql, vid)
        eschema = self._cw.vreg.schema.eschema(self.etype)
        if eschema.has_perm(req, 'add'):
            actions.append(self.mk_action(_('create basket'),
                                          self.create_url(self.etype),
                                          category='manage'))
        if not box.is_empty():
            box.render(self.w)


class SelectBasketContentAction(action.Action):
    category = 'mainactions'
    __select__ = implements('Basket')

    __regid__ = 'select_basket_content'
    title = _('actions_select_basket_content')

    def url(self):
        rql = u'Any X WHERE X in_basket B, B eid %s' % self.cw_rset[self.cw_row or 0][self.cw_col or 0]
        return self._cw.build_url(rql=rql)


