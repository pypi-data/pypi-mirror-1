##############################################################################
# Copyright 2008, Gerhard Weis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT
##############################################################################
'''
This modules provides a function to load  WSDL document from an url and return
and IServiceDescription (IWSDL) from it.
'''
from urllib2 import urlopen

from lxml import etree

from rsl.globalregistry import lookupimpl
from rsl.misc.namespace import clark2tuple
from rsl.wsdl.interfaces import IWSDL

def loadWSDL(url):
    """
    loads and parses a wsdl and returns an IWSDL instance. this function can
    handle multiple WSDL versions.
    
    @param url: The url from where to load the wsdl.
    @type url: C{string}
    
    @return: Returns a Service object created from the wsdl.
    @rtype: L{WSDL}    
    """
    fobj = urlopen(url)
    data = fobj.read()
    fobj.close()
    root = etree.fromstring(data)
    xns, _ = clark2tuple(root.tag)
    wsdlfactory = lookupimpl(IWSDL, xns)
    return wsdlfactory(url).frometree(root)

