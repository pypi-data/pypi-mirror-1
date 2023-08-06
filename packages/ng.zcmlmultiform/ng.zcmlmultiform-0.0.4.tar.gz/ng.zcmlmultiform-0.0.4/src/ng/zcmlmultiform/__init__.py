### -*- coding: utf-8 -*- #############################################
# $Id: __init__.py 51584 2008-08-31 14:51:11Z cray $
#######################################################################

# Make it a Python package

import os
default_template_path = os.path.abspath(os.path.join(os.path.join(*__path__),'multiformitem.pt'))
default_multitemplate_path = os.path.abspath(os.path.join(os.path.join(*__path__),'multiform.pt'))
