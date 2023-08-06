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
        
        if num_args != 2:
            raise TracError('Incorrect number of arguments (two required). Usage: [[subpage(true/false, page)]] where true/false determines whether or not an Edit Section link is shown.')
            
        edit_link = content.split(',')[0].lower().strip()
        wiki_page = content.split(',')[1].strip()

        if not edit_link in ('true', 'false'):
            raise TracError('Incorrect first argument (should be "true" or "false"). Usage: [[subpage(true/false, page)]] where true/false determines whether or not an Edit Section link is shown.')
        edit_link = edit_link == 'true'
        
        # FIXME: The error raised if the wiki page doesn't exist isn't descriptive at all
        target_url = formatter.wikiparser.link_resolvers['wiki'](formatter, 'wiki', wiki_page, None).attrib.get('href')
        
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("SELECT text FROM wiki WHERE wiki.name = '%s' ORDER BY wiki.version DESC LIMIT 1;" % (wiki_page))

        body = format_to_html(self.env, formatter.context, [page for page in cursor][0][0])
            
        if edit_link:
            return str(body) + (edit_link and'<p><a href="' + target_url + '?action=edit" class="wiki">Edit Section</a></p>')

