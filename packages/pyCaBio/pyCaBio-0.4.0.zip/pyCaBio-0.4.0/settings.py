
# The location of the input WSDL
WSDL_FILE = "conf/cabio42.wsdl"

# Root package for the resulting API 
ROOT_PACKAGE = "cabig.cabio"

# Mapping from Java to Python packages 
# The ROOT_PACKAGE is prepended to each Python package
PACKAGE_MAPPING = {
    'gov.nih.nci.cabio.domain' : 'domain',
    'gov.nih.nci.cabio.pathways' : 'pathways',
    'gov.nih.nci.common.domain' : 'common.domain',
    'gov.nih.nci.common.provenance.domain' : 'common.provenance.domain',
}

SERVICE_CLASS_NAME = "CaBioApplicationService"

OUTPUT_DIR = "output"
