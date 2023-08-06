##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


import os
from zope.interface import Interface, implements

# initialize/register all HTML transformations
import zopyx.smartprintng.core.transformation
from zopyx.smartprintng.core.highlevel import convert
from zopyx.smartprintng.core.interfaces import IImageFetcher
from zopyx.smartprintng.core.adapters import ExternalImageFetcher

from zope.app.testing import ztapi

from zopyx.smartprintng.core.renderer import Renderer
from zopyx.smartprintng.core.interfaces import IImageFetcher
from zopyx.smartprintng.core.adapters import ExternalImageFetcher


class ITestContent(Interface):
    pass

class TestContent(object):
    implements(ITestContent)

ztapi.provideAdapter(ITestContent, IImageFetcher, ExternalImageFetcher)

# register resources directory for demo purposes 
from zopyx.smartprintng.core import resources

def main():
    resources_configuration_file = os.path.join(os.path.dirname(__file__), 'resources', 'resources.ini')
    resources.registerResource(ITestContent, resources_configuration_file)

    from zopyx.convert2.registry import availableConverters

    for fullname in ('Andreas Jung', 'Heinz Becker', 'Hilde Becker'):

        context = TestContent()
        result = convert(context=context,
                         html='',
                         styles=['business_card.css'],
                         resource_name='demo',
                         converter='pdf-prince',
                         template_options=dict(fullname=fullname),
                         destination_filename=os.path.join(os.getcwd(), '%s.pdf' % fullname),
                        )
                        
        print 'Generated:', os.path.abspath(result)
        print

if __name__ == '__main__':
    import sys
    sys.exit(main())
