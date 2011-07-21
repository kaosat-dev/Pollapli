from twisted.web.template import Element, renderer, XMLFile

class ExampleElement(Element):
    loader = XMLFile('pollapli_ui_template.xml')

    @renderer
    def header(self, request, tag):
        return tag('Header.', id='header')

    @renderer
    def footer(self, request, tag):
        return tag('Footer.', id='footer')
