
from flask import Blueprint, render_template, make_response, current_app, request
from flask_menu import register_menu, current_menu
from flask_breadcrumbs import register_breadcrumb

from invenio.base.i18n import _
from invenio.base.signals import pre_template_render
from invenio.ext.template. \
    context_processor import register_template_context_processor

blueprint = Blueprint('lw_daap', __name__, url_prefix='',
                      template_folder='templates', static_folder='static')


#
# Main
#
@blueprint.route('/', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.project', _("Project"))
def project():
    return render_template('lw_daap/project.html')

#
# Footer
#
@blueprint.route('/about', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.about', _("About"))
def about():
    return render_template('lw_daap/about.html')

@blueprint.route('/dev', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.api', _("API"))
def api():
    return render_template('lw_daap/api.html')

@blueprint.route('/styles', methods=['GET', ])
def styles():
    return render_template('lw_daap/styles.html')

@blueprint.route('/contact', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.contact', _("Contact"))
def contact():
    return render_template('lw_daap/contact.html')

@blueprint.route('/privacypolicy', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.privacypolicy', _("Privacy Policy"))
def privacypolicy():
    return render_template('lw_daap/privacypolicy.html')

@blueprint.route('/termsofservices', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.termsofservices', _("Terms of Services"))
def termsofservices():
    return render_template('lw_daap/termsofservices.html')
#
#
#

@blueprint.before_app_first_request
def register_menu_items():
    def menu_fixup():
        item = current_menu.submenu('settings.profile')
        item.register(
            'userProfile.index', _('%(icon)s Profile', icon='<i class="fa fa-user fa-fw"></i>'),
            order=0,
            active_when=lambda: request.endpoint.startswith("userProfile."),
        )
    current_app.before_first_request_funcs.append(menu_fixup)


def add_record_variables(sender, **kwargs):
    """Add a variable 'daap_files' and 'daap_record' into record templates."""
    if 'recid' not in kwargs:
        return

    @register_template_context_processor
    def _add_record_variables():
        from invenio.legacy.bibdocfile.api import BibRecDocs
        from invenio.modules.records.api import get_record

        ctx = dict(
            daap_files=[f for f in BibRecDocs(
                kwargs['recid'], human_readable=True
            ).list_latest_files(
                list_hidden=False
            ) if not f.is_icon()],
            # this updates the DB, but avoids ugly caching
            daap_record=get_record(kwargs['recid'], True)
        )

        return ctx


@blueprint.before_app_first_request
def register_receivers():
    # Add template context processor to record request, that will add a files
    # variable into the template context
    pre_template_render.connect(add_record_variables, 'record.metadata')
    pre_template_render.connect(add_record_variables, 'record.files')
    pre_template_render.connect(add_record_variables, 'record.usage')


@blueprint.route('/collection/Dataset/dcat', methods=['GET', ])
def dcat():
    from invenio.legacy.search_engine import perform_request_search
    from invenio.modules.records.api import get_record
    from invenio.modules.formatter.api import get_modification_date, get_creation_date
    from invenio.utils.mimetype import guess_mimetype_and_encoding, guess_extension

    recids = perform_request_search(cc='Dataset')
    dcat =     """<rdf:RDF\n"""
    dcat +=    """   xmlns:dc="http://purl.org/dc/elements/1.1/"\n"""
    dcat +=    """   xmlns:dcat="http://www.w3.org/ns/dcat#"\n"""
    dcat +=    """   xmlns:dct="http://purl.org/dc/terms/"\n"""
    dcat +=    """   xmlns:foaf="http://xmlns.com/foaf/0.1/"\n"""
    dcat +=    """   xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n"""
    dcat +=    """   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n"""
    dcat +=    """   xmlns:owl="http://www.w3.org/2002/07/owl#"\n"""
    dcat +=    """   xmlns:time="http://www.w3.org/2006/time#"\n"""
    dcat +=    """   xmlns:prism="http://prismstandard.org/namespaces/basic/3.0/"\n"""
    dcat +=    """   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n"""
    dcat +=    """      <dcat:Catalog rdf:about=\"""" + current_app.config['CFG_SITE_URL'] + """/collection/Dataset">\n"""
    dcat +=    """         <dc:language>""" + current_app.config['CFG_SITE_LANG'] + """</dc:language>\n"""
    dcat +=    """         <dct:title xml:lang=\"""" + current_app.config['CFG_SITE_LANG'] + """\">""" + current_app.config['CFG_SITE_NAME'] + """</dct:title>\n"""
    dcat +=    """         <dct:description xml:lang=\"""" + current_app.config['CFG_SITE_LANG'] + """\">""" + current_app.config['CFG_SITE_DESCRIPTION'] + """</dct:description>\n"""
    dcat +=    """         <dct:extent>\n"""
    dcat +=    """            <dct:SizeOrDuration>\n"""
    dcat +=    """               <rdf:value rdf:datatype="http://www.w3.org/2001/XMLSchema#nonNegativeInteger">""" + str(len(recids)) + """</rdf:value>\n"""
    dcat +=    """                  <rdfs:label xml:lang=\"""" + current_app.config['CFG_SITE_LANG'] + """\">""" + str(len(recids)) + """ datasets</rdfs:label>\n"""
    dcat +=    """            </dct:SizeOrDuration>\n"""
    dcat +=    """         </dct:extent>\n"""
    dcat +=    """         <foaf:homepage rdf:resource=\"""" + current_app.config['CFG_SITE_URL'] + """\"/>\n"""
    dcat +=    """         <dct:publisher rdf:resource="http://www.lifewatch.eu/"/>\n"""
    dcat +=    """         <dcat:themeTaxonomy rdf:resource="http://datos.gob.es/kos/sector-publico/sector/medio-rural-pesca"/>\n"""
    dcat +=    """         <dcat:themeTaxonomy rdf:resource="http://datos.gob.es/kos/sector-publico/sector/medio-ambiente"/>\n"""

    issues = []
    modifications = []
    for recid in recids:
       issues.append(get_creation_date(recid))
       modifications.append(get_modification_date(recid))

    dcat +=    """         <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">""" + str(min(issues)) + """</dct:issued>\n"""
    dcat +=    """         <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">""" + str(max(modifications)) + """</dct:modified>\n"""

    for recid in recids:
       record = get_record(recid)
       dcat += """         <dcat:dataset>\n"""

       if 'doi' in record:
          dcat += """            <dcat:Dataset rdf:about="http://dx.doi.org/""" +  str(record['doi']) + """\">\n"""
          dcat += """               <dct:identifier>http://dx.doi.org/""" +  str(record['doi']) + """</dct:identifier>\n"""
       else:
          dcat += """            <dcat:Dataset rdf:about=\"""" + current_app.config['CFG_SITE_URL'] + """/""" + current_app.config['CFG_SITE_RECORD'] + """/""" + str(recid) + """">\n"""
          dcat += """               <dct:identifier>""" + current_app.config['CFG_SITE_URL'] + """/""" + current_app.config['CFG_SITE_RECORD'] + """/""" + str(recid) + """     </dct:identifier>\n"""

       dcat += """               <dct:title xml:lang=\"""" + current_app.config['CFG_SITE_LANG'] + """\">""" + str(record['title']) + """</dct:title>\n"""
       dcat += """               <dct:description xml:lang=\"""" + current_app.config['CFG_SITE_LANG'] + """\">""" + str(record['description']) + """</dct:description>\n"""
       dcat += """               <dcat:theme rdf:resource=""/>\n"""
       dcat += """               <dc:language>""" + current_app.config['CFG_SITE_LANG'] + """</dc:language>\n"""
       dcat += """               <dct:publisher rdf:resource="http://www.lifewatch.eu/"/>\n"""

       if record['access_right'] <> 'restricted' and record['access_right'] <> 'closed':
          if 'url' in record['__license_text__']:
             dcat += """               <dct:license rdf:resource=\"""" + str((record['__license_text__'])['url']) + """\"/>\n"""

       if 'embargo_date' in record:
          dcat += """               <prism:embargoDate rdf:datatype="http://www.w3.org/2001/XMLSchema/#date">""" + str(record['embargo_date']) + """</prism:embargoDate>\n"""

       for kw in record['keywords']:
          dcat += """               <dcat:keyword>""" + str(kw) + """</dcat:keyword>\n"""

       dcat += """               <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#date">""" + str(get_creation_date(recid)) + """</dct:issued>\n"""
       dcat += """               <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#date">""" + str(get_modification_date(recid)) + """</dct:modified>\n"""

       if 'period' in record:
          for period in record['period']:
             dcat += """               <dct:temporal>\n"""
             dcat += """                  <time:Interval>\n"""
             dcat += """                     <rdf:type rdf:resource="http://purl.org/dc/terms/PeriodOfTime" />\n"""
             dcat += """                     <time:hasBeginning>\n"""
             dcat += """                        <time:Instant>\n"""
             dcat += """                           <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">""" + str(period['start']) + """</time:inXSDDateTime>\n"""
             dcat += """                           </time:inXSDDateTime>\n"""
             dcat += """                        </time:Instant>\n"""
             dcat += """                     </time:hasBeginning>\n"""
             dcat += """                     <time:hasEnd>\n"""
             dcat += """                        <time:Instant>\n"""
             dcat += """                           <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">""" + str(period['end']) + """</time:inXSDDateTime>\n"""
             dcat += """                        </time:Instant>\n"""
             dcat += """                     </time:hasEnd>\n"""
             dcat += """                  </time:Interval>\n"""
             dcat += """               </dct:temporal>\n"""

       if 'fft' in record:
          for dis in record['fft']:
             dcat += """               <dcat:distribution>\n"""
             dcat += """                  <dcat:Distribution rdf:about="">\n"""

             if 'description' in dis:
                dcat += """                     <dct:title xml:lang="en">""" + str(dis['description']) + """</dct:title>\n"""

             dcat += """                     <dct:accessURL  rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">""" + str(dis['url']) + """</dct:accessURL>\n"""
             dcat += """                     <dct:format>\n"""
             mimetype = str(guess_mimetype_and_encoding(dis['url'])[0])
             dcat += """                        <dct:IMT rdf:value=\"""" + mimetype + """\" rdfs:label=\"""" + str(guess_extension(mimetype)[1:]).upper() + """\"/>\n"""
             dcat += """                     </dct:format>\n"""
             dcat += """                     <dcat:byteSize rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">""" + str(dis['file_size']) + """</dcat:byteSize>\n"""
             dcat += """                  </dcat:Distribution>\n"""
             dcat += """               </dcat:distribution>\n"""

       dcat += """            </dcat:Dataset>\n"""
       dcat += """         </dcat:dataset>\n"""

    dcat += """      </dcat:Catalog>\n"""
    dcat += """   </rdf:RDF>"""

    response = make_response(dcat)
    response.headers["Content-Disposition"] = "attachment; filename=dcat.rdf"
    return response

