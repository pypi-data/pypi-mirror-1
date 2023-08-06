from Products.CMFCore.utils import getToolByName

def import_various(context):
    
    if not context.readDataFile('inqbus.plone.panorama.txt'):
        return
        
    site = context.getSite()
    kupu = getToolByName(site, 'kupu_library_tool')
    paragraph_styles = list(kupu.getParagraphStyles())
    
    new_styles = [('panorama', 'Panorama image|img')]
    to_add = dict(new_styles)
    
    for style in paragraph_styles:
        css_class = style.split('|')[-1]
        if css_class in to_add:
            del to_add[css_class]

    if to_add:
        paragraph_styles += ['%s|%s' % (v, k) for k,v in new_styles if k in to_add]
        kupu.configure_kupu(parastyles=paragraph_styles)

    print "inqbus.plone.panorama: set 'Allow original size images' for Kupu"
    kupu.configure_kupu(allowOriginalImageSize=True)
