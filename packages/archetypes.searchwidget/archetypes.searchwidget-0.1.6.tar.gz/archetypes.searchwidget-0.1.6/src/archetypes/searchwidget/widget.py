
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Widget import ReferenceWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Registry import registerPropertyType

from collective.searchtool.interfaces import ISearchProvider
from archetypes.searchwidget import MessageFactory as _


class SearchWidget(ReferenceWidget):
    """ for documentation of properties see: README.txt """

    _properties = ReferenceWidget._properties.copy()
    _properties.update({
        'macro': 'searchwidget',
        'button_label': 'Add / Remove',
        'clearbutton_label': 'Clear Selection',
        'searchforms': ('searchwidget-images',
                        'searchwidget-files',
                        'searchwidget-documents',),
        'helper_js': ('++resource++jquery.ui/ui/ui.core.js',
                      '++resource++jquery.ui/ui/ui.dialog.js',
                      '++resource++jquery.ui/ui/ui.draggable.js',
                      '++resource++jquery.ui/ui/ui.resizable.js',
                      '++resource++jquery.ui/ui/ui.tabs.js',),
        'helper_css': ('++resource++jquery.ui/themes/base/ui.all.css',
                       '++resource++archetypes.searchwidget/smoothness/ui.all.css',
                       '++resource++archetypes.searchwidget/custom.css',),
        'popup_width': '500',
        'popup_height': '550',
        })

    def get_property(self, fieldname):
        return getattr(self, fieldname, self._properties[fieldname])
        
    def popup_javascript(self, context, request, site_url, fieldname, multiValued=False):
        select_item, multi_select = '', ''
        if multiValued == False:
            select_item = '''
                jq("#searchwidget-%(fieldname)s-popup .searchwidget-selected").removeClass("searchwidget-selected");  
                jq(this).addClass('searchwidget-selected');
                ''' % {'fieldname': fieldname}
        else:
            multi_select = '''
                jq('<ul class="searchwidget-multiselect"></ul>').prependTo(jq("#searchwidget-%(fieldname)s-popup"));
                jq('#archetypes-fieldname-%(fieldname)s ul.searchwidget-selected > li').clone().appendTo("#searchwidget-%(fieldname)s-popup ul.searchwidget-multiselect");
                jq("#searchwidget-%(fieldname)s-popup ul.searchwidget-multiselect > li").addClass('searchwidget-selected').click(function() { jq(this).remove(); return false; });
                    ''' % {'fieldname': fieldname}
            select_item = '''
                var UID = jq(this).find('a').attr('alt');
                if (jq('#searchwidget-%(fieldname)s-popup ul.searchwidget-multiselect > li > a').is('[alt="'+UID+'"]')) { return false; }
                var title = jq(this).find('span').text();
                var image_src = jq(this).find('img').attr('src');
                /*if (image_src.match('image_thumb$') == 'image_thumb') {
                    image_src = image_src.replace('image_thumb', 'image_icon');
                }*/
                var popup_item = jq('<li class="searchwidget-selected"><a alt="'+UID+'"><img src="'+image_src+'" /><span>'+title+'</span></a></li>');

                popup_item.appendTo(jq('#searchwidget-%(fieldname)s-popup ul.searchwidget-multiselect'));
                popup_item.click(function() {
                    jq(this).remove();
                    return false;
                });
                ''' % {'fieldname': fieldname}
        
        searchwidget_forms = ['', '', '']
        for formname in getattr(self, 'searchforms', self._properties['searchforms']):
            form = getMultiAdapter((context, request, None), ISearchProvider, formname)
            searchwidget_forms[0] += '<li><a href="#searchwidget-%s-%s-form"><span>%s</span></a></li>' % (fieldname, formname, form.label)
            searchwidget_forms[1] += '<div id="searchwidget-%s-%s-form"></div>' % (fieldname, formname)
            searchwidget_forms[2] += '''
                jq("#searchwidget-%(fieldname)s-%(formname)s-form").load(
                        "%(site_url)s/++search++%(formname)s", {}, function() {
                    jq("#searchwidget-%(fieldname)s-%(formname)s-form #form-buttons-search").click(function() {
                        jq("#searchwidget-%(fieldname)s-popup .searchwidget-results").load(
                                "%(site_url)s/++search++%(formname)s?form.buttons.search=1&"+
                                jq("#searchwidget-%(fieldname)s-%(formname)s-form .field input").serialize()+
                                " .seachResultPage", null, function() {
                            jq("#searchwidget-%(fieldname)s-popup dd").click(function() {
                                %(select_item)s;
                                return false;
                            });
                            jq("#searchwidget-%(fieldname)s-popup .searchResults").height(jq("#searchwidget-%(fieldname)s-popup").height()-jq("#searchwidget-%(fieldname)s-popup .searchwidget-forms").height()-jq("#searchwidget-%(fieldname)s-popup .searchwidget-results h1").height()-11);
                        });
                        return false;
                    });
                    jq("#searchwidget-%(fieldname)s-popup .searchwidget-multiselect").height(jq("#searchwidget-%(fieldname)s-popup").height()-40);
                });
                ''' % {'fieldname':     fieldname,
                       'formname':      formname,
                       'site_url':      site_url,
                       'select_item':   select_item,}

        searchwidget_forms = '''
            %(multi_select)s
            jq('#searchwidget-%(fieldname)s-popup .searchwidget-forms').replaceWith(jq('<div class="searchwidget-forms"><ul style="height: 30px;">%(tabs)s</ul>%(forms)s</div>'));
            %(forms_js)s
            jq("#searchwidget-%(fieldname)s-popup .searchwidget-forms > ul").tabs();
            jq("#searchwidget-%(fieldname)s-popup .searchResults").height(jq("#searchwidget-%(fieldname)s-popup").height()-jq("#searchwidget-%(fieldname)s-popup .searchwidget-forms").height()-jq("#searchwidget-%(fieldname)s-popup .searchwidget-results h1").height()-11);
            ''' % {'fieldname':     fieldname,
                   'tabs':          searchwidget_forms[0],
                   'forms':         searchwidget_forms[1],
                   'forms_js':      searchwidget_forms[2],
                   'multi_select':  multi_select, }

        return '''
            jq("#searchwidget-%(fieldname)s-clearbutton").click(function() {
                jq("ul.searchwidget-selected > li").remove();
                return false;
            });
            jq("#searchwidget-%(fieldname)s-button").click(function() {
                jq("#searchwidget-%(fieldname)s-popup").dialog({
                    modal:      true,
                    overlay:    {opacity: 0.5, background: "black"},
                    position:   ["center", "center"],
                    height:     %(popup_height)s,
                    width:      %(popup_width)s,
                    resizeStop:     function() {
                        jq("#searchwidget-%(fieldname)s-popup .searchResults").height(jq("#searchwidget-%(fieldname)s-popup").height()-jq("#searchwidget-%(fieldname)s-popup .searchwidget-forms").height()-jq("#searchwidget-%(fieldname)s-popup .searchwidget-results h1").height()-11);
                        jq("#searchwidget-%(fieldname)s-popup .searchwidget-multiselect").height(jq("#searchwidget-%(fieldname)s-popup").height()-40);
                    },
                    close:      function(event, options) {
                        jq(this).dialog("destroy").remove();
                        jq('<div class="searchwidget-popup%(multi_style)s" style="display: none;" id="searchwidget-%(fieldname)s-popup"><div class="searchwidget-forms"></div><div class="searchwidget-results"></div></div>').appendTo(jq("#archetypes-fieldname-%(fieldname)s"));
                    },
                    open:       function(event, object) {
                        jq(this).css("display", "block");
                        %(searchwidget_forms)s
                    },
                    buttons: {
                        'Cancel': function() {
                            jq(this).dialog("close");
                        },
                        'OK': function() {
                            jq("#archetypes-fieldname-%(fieldname)s ul > li").remove();
                            jq('#searchwidget-%(fieldname)s-popup .searchwidget-selected').each(function() {
                                var UID = jq(this).find('a').attr('alt');
                                if (jq('#archetypes-fieldname-%(fieldname)s ul > li > a').is('[alt="'+UID+'"]')) { return false; };

                                var title = jq(this).find('a > span').text();
                                var image_src = jq(this).find('img').attr('src');
                                //if (image_src.match('image_thumb$') == 'image_thumb') {
                                //    image_src = image_src.replace('image_thumb', 'image_icon');
                                //}

                                jq('#searchwidget-%(fieldname)s-popup ul.searchwidget-popup-selected > li').remove();
                                var field_item = jq('<li><a alt="'+UID+'"><img src="'+image_src+'" /><span>'+title+'</span><inp'+'ut type="hidden" value="'+UID+'" name="%(fieldname)s:default:list" /></a></li>');
                                field_item.appendTo(jq('#archetypes-fieldname-%(fieldname)s ul.searchwidget-selected'));

                            });
                            jq(this).dialog("close");
                        }
                    }
                });
                return false;
            });''' % {'fieldname':          fieldname,
                      'popup_height':       getattr(self,'popup_height',self._properties['popup_height']),
                      'popup_width':        getattr(self,'popup_width',self._properties['popup_width']),
                      'searchwidget_forms': searchwidget_forms,
                      'multi_style':        multiValued and '-multi' or '',}
            
    def render_item(self, uid, title, icon='', extra=''):
        return '''
            <a alt="%(uid)s" href="#">
                %(icon)s<span>%(title)s</span>%(extra)s
            </a>''' % {'uid': uid, 'title': title, 'extra': extra,
                       'icon': icon and '<img src="'+icon+'" />' or ''}

    def references(self, context, items):
        return getToolByName(context, 'portal_catalog')(UID=items)


registerWidget(SearchWidget,
               title=_('Search Reference'),
               description=(_('Search for references.')),
               used_for=('Products.Archetypes.Field.ReferenceField',))

registerPropertyType('searchforms', 'lines', SearchWidget)
registerPropertyType('helper_js', 'lines', SearchWidget)
registerPropertyType('helper_css', 'lines', SearchWidget)
registerPropertyType('popup_width', 'string', SearchWidget)
registerPropertyType('popup_height', 'string', SearchWidget)

