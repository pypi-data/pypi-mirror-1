from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
            
setup(name='huBarcode',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='http://www.hosted-projects.com/trac/hudora/public/wiki/huBarcode',
      version='0.5',
      description='generation of barcodes in Python',
      classifiers=['License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Topic :: Multimedia :: Graphics',
                   'Topic :: Office/Business'],
      package_dir = {'huBarcode': ''},
      packages=['huBarcode', 'huBarcode.qrcode', 'huBarcode.qrcode.data', 'huBarcode.datamatrix'],
      
)
