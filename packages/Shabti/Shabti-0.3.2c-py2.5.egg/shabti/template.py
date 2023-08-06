from paste.script import templates
from tempita import paste_script_template_renderer

class ShabtiTemplate(templates.Template):
    egg_plugins = [ 'Shabti', 'Elixir']
    required_templates = ['pylons']
    _template_dir = 'templates/default'
    summary = 'Pylons + Elixir template'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiAuthTemplate(templates.Template):
    required_templates = ['shabti']
    _template_dir = 'templates/auth'
    summary = 'Shabti + simple authentication'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiAuthXpTemplate(templates.Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/auth_xp'
    summary = 'Shabti + row-level authentication (experimental)'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiAuthCouchdbTemplate(templates.Template):
    required_templates = ['pylons']
    _template_dir = 'templates/auth_couchdb'
    summary = 'Shabti auth using CouchDB'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiRDFAlchemyTemplate(templates.Template):
    required_templates = ['pylons']
    _template_dir = 'templates/rdfalchemy'
    summary = 'Pylons + RDFAlchemy template'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiAuthRepozeWhoTemplate(templates.Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/auth_repozewho'
    summary = 'Shabti auth using repoze.who'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiAuthRepozeWhatTemplate(templates.Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/auth_repozewhat'
    summary = 'Shabti auth using repoze.what'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiAuthRepozePylonsTemplate(templates.Template):
    required_templates = ['shabti']
    _template_dir = 'templates/auth_repozepylons'
    summary = 'auth + auth using repoze.what and repoze.who'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiAuthkitTemplate(templates.Template):
    required_templates = ['shabti']
    _template_dir = 'templates/authkit'
    summary = "Shabti auth'n'auth using authkit"
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiAuthRDFAlchemyTemplate(templates.Template):
    required_templates = ['shabti']
    _template_dir = 'templates/auth_rdfalchemy'
    summary = "Shabti auth'n'auth using RDFAlchemy"
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiMicroSiteTemplate(templates.Template):
    required_templates = ['pylons']
    _template_dir = 'templates/microsite'
    summary = 'Pylons + auth + tw + templates + css'
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiSemWebTemplate(templates.Template):
    required_templates = ['shabti_auth_rdfalchemy']
    _template_dir = 'templates/semweb'
    summary = "Shabti Semantic Web starter kit"
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiQuickWikiTemplate(templates.Template):
    required_templates = ['shabti']
    _template_dir = 'templates/quickwiki'
    summary = "Shabti *quick* QuickWiki"
    template_renderer = staticmethod(paste_script_template_renderer)

class ShabtiBlogTemplate(templates.Template):
    required_templates = ['shabti_auth']
    _template_dir = 'templates/blog'
    summary = "Shabti blog"
    template_renderer = staticmethod(paste_script_template_renderer)


