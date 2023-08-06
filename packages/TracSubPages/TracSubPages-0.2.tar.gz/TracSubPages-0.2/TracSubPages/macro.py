from trac.core import Component, TracError, implements
from trac.wiki.api import IWikiMacroProvider
from trac.wiki.formatter import format_to_html
from trac.wiki.parser import WikiParser
from pkg_resources import resource_filename


class SubPageMacro(Component):
    implements(IWikiMacroProvider)
    
    # IWikiMacroProvider methods
    def get_macros(self):
        return ['subpage']
    
    def get_macro_description(self, name):
        return 'A Trac macro to display bodies of other wiki pages inline'

    def expand_macro(self, formatter, name, content):
        num_args = len(content.split(','))
        
        if not (1 <= num_args <= 2):
            raise TracError(('Incorrect number of arguments (two required). '
                             'Usage: [[subpage(page, [true/false])]] where '
                             'true/false determines whether or not an Edit '
                             'Section link is shown.'))
        
        wiki_page = content.split(',')[0].strip()
        
        if num_args == 2:
            edit_link = content.split(',')[1].lower().strip()
            if not edit_link in ('true', 'false'):
                raise TracError(('Incorrect second argument (should be "true" '
                                 'or "false"). Usage: [[subpage(true/false, '
                                 'page)]] where true/false determines whether '
                                 'or not an Edit Section link is shown.'))
            edit_link = edit_link == 'true'
        
        else:
            edit_link = True
        
        # TODO: The error raised if the wiki page
        #       doesn't exist isn't descriptive at all
        wikiparser = formatter.wikiparser
        target_url = wikiparser.link_resolvers['wiki'](formatter, 
                                                       'wiki', 
                                                       wiki_page, 
                                                       None).attrib.get('href')
        
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute(("SELECT text FROM wiki WHERE wiki.name = '%s' ORDER BY "
                        "wiki.version DESC LIMIT 1;") % (wiki_page))
                        
        wiki_body = [page for page in cursor][0][0]
        body = format_to_html(self.env, formatter.context, wiki_body)
        
        link_tag = ('<p><a href="%s?action=edit" class="wiki">Edit Section</a>'
                    '</p>' % (target_url))
            
        return str(body) + (edit_link and link_tag or '')


