"""Specific views for tag

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import html_escape

from cubicweb.selectors import (match_context_prop, match_kwargs,
                                match_form_params, match_user_groups,
                                has_related_entities, one_etype_rset,
                                implements, relation_possible)
from cubicweb import uilib, tags
from cubicweb.web import uicfg, stdmsgs, component, box, facet
from cubicweb.web.htmlwidgets import BoxWidget, BoxHtml
from cubicweb.web.views import baseviews, basecontrollers


uicfg.autoform_section.tag_subject_of(('*', 'tags', '*'), formtype='main', section='hidden')
uicfg.autoform_section.tag_object_of(('*', 'tags', '*'), formtype='main', section='hidden')
# displayed by the above component or box, don't display it in primary view
uicfg.primaryview_section.tag_subject_of(('*', 'tags', '*'), 'hidden')
uicfg.primaryview_section.tag_object_of(('*', 'tags', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Tag', 'tags', '*'), 'relations')
uicfg.primaryview_section.tag_attribute(('Tag', 'name'), 'hidden')


class TagInContextView(baseviews.InContextView):
    __regid__ = 'incontext'
    __select__ = implements('Tag')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(entity.view('textincontext'), href=entity.absolute_url(),
                      title=uilib.cut(entity.dc_description(), 50), rel=u'tag'))


class TagCloudView(baseviews.OneLineView):
    """cloud view to make a link on tagged entities appearing more or less big
    according to the number of tagged entities

    expect a result set with tag eid in the first column and number of tagged
    objects in the second column.
    expect as well:
    * `maxsize` argument, the maximum number of tagged entities by a tag in the
      cloud
    * `etype` argument, the entity type we are filtering
    """
    __regid__ = 'tagcloud'
    __select__ = implements('Tag') & (match_kwargs('etype')
                                      | match_form_params('etype'))

    need_navigation = False
    add_div_section = False # configure View.call behaviour

    onload_js = '''
jQuery(document).tagcloud.defaults = {
  size: {start: 0.8, end: 2.5, unit: "em"},
  color: {start: "#333", end: "#FF7700"}
};
jQuery("#tagcloud a").tagcloud();
'''
    def call(self, *args, **kwargs):
        self._cw.add_css('cubes.tag.css')
        self._cw.add_js(('cubes.tag.js', 'jquery.tagcloud.js'))
        self._cw.html_headers.add_onload(self.onload_js)
        self.w(u'<div id="tagcloud">')
        super(TagCloudView, self).call(*args, **kwargs)
        self.w(u'</div>')

    def cell_call(self, row, col, etype=None, **kwargs):
        if etype is None:
            etype = self._cw.form['etype']
        entity = self.cw_rset.get_entity(row, col)
        mysize = self.cw_rset[row][1]
        # generate url according to where it is called from eg. when browsing
        # blogs the tag box should point to Blogs tagged by...
        rql = 'Any X WHERE T tags X, T eid %s, X is %s' % (entity.eid, etype)
        # XXX rel=mysize, can't we set rel='tag %s' % mysize to get back the
        #     'tag' rel?
        self.w(tags.a(entity.name, rel=mysize,
                      href=self._cw.build_url('view', rql=rql))+ u' ')


# components and boxes to view and edit tag of taggable entities ###############

class ClosestTagsBox(box.EntityBoxTemplate):
    __regid__ = 'closest_tags_box'
    __select__ = box.EntityBoxTemplate.__select__ & implements('Tag',)
    order = 25

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        closest_tags = entity.closest_tags_rset()
        if closest_tags:
            self.w(u'<div class="sideBox">')
            self.wview('sidebox', closest_tags, title=self._cw._("Closest tags"))
            self.w(u'</div>')


class SimilarityBox(box.EntityBoxTemplate):
    """layout closest entities (ie. entities that share tags)"""
    __regid__ = 'similarity_box'
    __select__ = (box.EntityBoxTemplate.__select__
                  & has_related_entities('tags', 'object', 'Tag'))
    order = 21

    def cell_call(self, row, col, **kwargs):
        self._cw.add_js('cubicweb.ajax.js', 'cubes.tag.js')
        entity = self.cw_rset.get_entity(row,col)
        rql = ('Any Y,COUNT(T) GROUPBY Y ORDERBY 2 DESC %s '
               'WHERE X eid %%(x)s, T tags X, T tags Y, NOT Y eid %%(x)s')
        limit = self._cw.property_value('navigation.related-limit')
        rset = self._cw.execute(rql % ('LIMIT %s' % limit),
                                {'x': entity.eid}, 'x')
        if rset:
            w = self.w
            w(u'<div class="sideBox" id="%s%s">' % (self.__regid__, entity.eid))
            if rset.rowcount == 1:
                title = self._cw._('similar entity')
            else:
                title = self._cw._('similar entities')
            w(u'<div class="sideBoxTitle"><span>%s</span></div>' % title)
            w(u'<div class="sideBox"><div class="sideBoxBody">')
            self.wview('list', rset, subvid='outofcontext')
            url = self._cw.build_url('view', rql=rql % '' % {'x': entity.eid},
                                     vtitle=_('entities similar to %s') % entity.dc_title())
            w(u'<div>[%s]</div>' % tags.a(self._cw._('see all'), href=url))
            w(u'</div>')
            w(u'</div>')
            w(u'</div>')



class TagsBox(box.EntityBoxTemplate):
    """the tag box: control tag of taggeable entity providing an easy way to
    add/remove tag
    """
    __regid__ = 'tags_box'
    __select__ = (box.EntityBoxTemplate.__select__
                  & relation_possible('tags', 'object', 'Tag'))

    order = 20

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        tags = entity.reverse_tags
        rdefs = entity.e_schema.rdef('tags', 'object', 'Tag')
        rschema = self._cw.vreg.schema.rschema('tags')
        addtag = rdefs.has_perm(self._cw, 'add', toeid=entity.eid)
        if not (tags or addtag):
            return
        self._cw.add_js(('cubicweb.ajax.js', 'cubes.tag.js'))
        _ = self._cw._
        w = self.w
        w(u'<div class="sideBox" id="%s%s">' % (self.__regid__, entity.eid))
        w(u'<div class="sideBoxTitle"><span>%s</span></div>' %
               rdefs.rtype.display_name(self._cw, 'object'))
        w(u'<div class="sideBox"><div class="sideBoxBody">')
        if tags:
            w(u'<table>')
            candelete = rdefs.has_perm(self._cw, 'delete', toeid=entity.eid)
            for tag in tags:
                # for each related keyword, provide a link to remove the tag
                subview = tag.view('incontext')
                if candelete:
                    editlink = u'[<a href="javascript:removeTag(%s, %s)">-</a>]'
                    w(u'<tr><td>%s</td><td class="tagged">%s</td></tr>'
                           % (editlink % (entity.eid, tag.eid), subview))
                else:
                    w(u'<tr><td class="tagged">%s</td></tr>' % (subview))
            w(u'</table>')
        else:
            w(_('no tag'))
        if addtag:
            self._cw.add_js('jquery.autocomplete.js')
            self._cw.add_css('jquery.autocomplete.css')
            w(u'<table><tr><td>')
            w('<a class="button sglink" href="javascript: showTagSelector'
              '(%s, \'%s\', \'%s\');">%s</a>' % (
                  entity.eid, _(stdmsgs.BUTTON_OK[0]), _(stdmsgs.BUTTON_CANCEL[0]),
                  _('add tag')))
            w(u'</td><td>')
            w(u'<div id="tagformholder%s"></div>' % entity.eid)
            w(u'</td></tr></table>')
        w(u'</div>\n')
        w(u'</div></div>\n')


class TagsCloudBox(box.BoxTemplate):
    """display a box with tag cloud for """
    __regid__ = 'tagcloud_box'
    __select__ = (box.BoxTemplate.__select__ & one_etype_rset() &
                  relation_possible('tags', 'object', 'Tag'))

    visible = False # disabled by default
    order = 30
    title = _('Tag_plural')
    context = 'left'

    def call(self, view=None, **kwargs):
        etype = iter(self.cw_rset.column_types(0)).next()
        # build rql as necessary for the tagcloud view
        tagrset = self._cw.execute('Any T,COUNT(X),TN GROUPBY T,TN LIMIT 30'
                                   'WHERE X is %s, T tags X, T name TN' % etype)
        if not tagrset:
            return
        html = self._cw.view('tagcloud', tagrset, etype=etype)
        rql = ('Any T,COUNT(X),TN GROUPBY T,TN '
               'WHERE X is %s, T tags X, T name TN' % etype)
        url = html_escape(self._cw.build_url(rql=rql, vid='tagcloud', etype=etype))
        box = BoxWidget(self._cw._(self.title).lower(), self.__regid__, islist=False)
        box.append(BoxHtml(html))
        box.append(BoxHtml(u'<div></div>'))
        see_more_link = u'[%s]' % tags.a(self._cw._('see all tags'), href=url)
        box.append(BoxHtml(see_more_link))
        box.render(self.w)


class MergeComponent(component.EntityVComponent):
    __regid__ = 'mergetag'
    __select__ = (component.EntityVComponent.__select__ &
                  implements('Tag') & match_user_groups('managers'))

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self._cw.add_js(('cubes.tag.merge.js', 'cubicweb.widgets.js',
                         'jquery.autocomplete.js',))
        self._cw.add_css('jquery.autocomplete.css')
        self.w(u'<hr/>')
        self.w(u'<div id="tagmergeformholder%s">' % entity.eid)
        self.w(u'<h5>%s</h5>'
               % self._cw._('merge tag with (choose tag and press enter)'))
        self.w(u'<input  type="hidden" id="tageid" value="%s"/>' % entity.eid)
        self.w(u'<input id="acmergetag" type="text" class="widget" cubicweb:dataurl="%s" '
               u'cubicweb:loadtype="auto" cubicweb:wdgtype="RestrictedSuggestField" />'
               % html_escape(self._cw.build_url('json', fname='unrelated_merge_tags',
                                            arg=entity.eid)))
        self.w(u'<div id="tagged_entities_holder"></div>')
        self.w(u'<div id="sgformbuttons" class="hidden">')
        self.w(u'<input class="validateButton" type="button" value="%s" onclick="javascript:mergeTags(%s);"/>'
               % ( self._cw._('merge'), entity.eid))
        self.w(u'<input class="validateButton" type="button" value="%s" onclick="javascript:cancelSelectedMergeTag(%s)"/>'
               % ( self._cw._(stdmsgs.BUTTON_CANCEL[0]), entity.eid))
        self.w(u'</div>')
        self.w(u'</div>')


# facets ######################################################################

class TagsFacet(facet.RelationFacet):
    __regid__ = 'tags-facet'
    rtype = 'tags'
    role = 'object'
    target_attr = 'name'


# add methods to the Jsoncontroller to add/remove tags on taggeable entities ###

@monkeypatch(basecontrollers.JSonController)
@basecontrollers.jsonize
def js_unrelated_tags(self, eid):

    """return tag unrelated to an entity"""
    rql = 'Any N ORDERBY N WHERE T is Tag, T name N, NOT T tags X, X eid %(x)s'
    return [name for (name,) in self._cw.execute(rql, {'x' : eid}, 'x')]


@monkeypatch(basecontrollers.JSonController)
def js_tag_entity(self, eid, taglist):
    execute = self._cw.execute
    # get list of tag for this entity
    tagged_by = set(tagname for (tagname,) in
                    execute('Any N WHERE T name N, T tags X, X eid %(x)s',
                            {'x': eid}, 'x'))
    for tagname in taglist:
        tagname = tagname.strip()
        if not tagname or tagname in tagged_by:
            continue
        tagrset = execute('Tag T WHERE T name %(name)s', {'name': tagname})
        if tagrset:
            rql = 'SET T tags X WHERE T eid %(t)s, X eid %(x)s'
            execute(rql, {'t': tagrset[0][0], 'x' : eid}, 'x')
        else:
            rql = 'INSERT Tag T: T name %(name)s, T tags X WHERE X eid %(x)s'
            execute(rql, {'name' : tagname, 'x' : eid}, 'x')

@monkeypatch(basecontrollers.JSonController)
def js_untag_entity(self, eid, tageid):
    rql = 'DELETE T tags X WHERE T eid %(t)s, X eid %(x)s'
    self._cw.execute(rql, {'t': tageid, 'x' : eid}, 'x')


# add methods to the Jsoncontroller to merge tags #############################

@monkeypatch(basecontrollers.JSonController)
@basecontrollers.jsonize
def js_unrelated_merge_tags(self, eid):
    """return tag unrelated to an entity"""
    rql = 'Any N ORDERBY N WHERE T is Tag, T name N, NOT T eid %(x)s'
    return [name for (name,) in self._cw.execute(rql, {'x' : eid}, 'x')]

@monkeypatch(basecontrollers.JSonController)
@basecontrollers.xhtmlize
def js_tagged_entity_html(self, name):
    rset = self._cw.execute('Any X ORDERBY X DESC LIMIT 10 WHERE T tags X, '
                            'T name %(x)s', {'x': name} )
    html = []
    if rset:
        html.append('<div id="taggedEntities">')
        #FIXME - add test to go through select_view
        view = self._cw.vreg['views'].select('list', self._cw, rset=rset)
        html.append(view.render(title=self._cw._('linked entities:')))
        html.append(u'</div>')
        # html.append(self._cw.view('list', rset))
    else:
        html.append('<div>%s</div>' %_('no entities related to this tag'))
        view = self._cw.vreg['views'].select('null', self._cw, rset=rset)
    return u' '.join(html)


@monkeypatch(basecontrollers.JSonController)
@basecontrollers.xhtmlize
def js_merge_tags(self, eid, mergetag_name):
    mergetag_name = mergetag_name.strip(',') # XXX
    self._cw.execute('SET T tags X WHERE T1 tags X, NOT T tags X, '
                     'T eid %(x)s, T1 name %(name)s',
                     {'x': eid, 'name': mergetag_name})
    self._cw.execute('DELETE Tag T WHERE T name %(name)s', {'name': mergetag_name})
    #FIXME - add test to go through select_view
    view = self._cw.vreg['views'].select('primary', self._cw, 
                                         rset=self._cw.eid_rset(eid))
    return view.render()
