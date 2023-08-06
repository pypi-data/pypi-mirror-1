## Script(Python) "getSection"
##bind container=container
##bind context=context
##title=Get the 1st level container of the context or site root
##

#
# Allow through-the-web visual editor support for footer.
# For each language, assume there exist a matching footer page content item
#
# portal_root/en-footer for English
# portal_root/fi-footer for Finnish
#

# Get the active two letter language code
boundLanguages=context.portal_languages.getLanguageBindings()
prefLang=boundLanguages[0]

footer_content_name = prefLang + "-footer"
if hasattr(context, footer_content_name):
    footer = getattr(context, footer_content_name)
    return footer.getText() 
else:
    return "Please create page named " + footer_content_name + " at portal root. It's body text is used as footer text."
