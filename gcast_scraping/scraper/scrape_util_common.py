import os, sys
import re
import unicodedata

def msg(m): print m

def dashes(): msg('-' *40)

def msgt(m): dashes(); msg(m); dashes();

def msgx(m):
    msgt('Error: %s' % m)
    msg('exiting..')
    sys.exit(0)

def poor_slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    
    return value.replace('\t', '-').replace(' ', '-')
    
    
def get_elem_by_href_only(driver, href):
    doc_xpath = "//a[@href='%s']" % href
    elem = driver.find_element_by_xpath(doc_xpath)
    return elem


def get_link_elem_by_href_text(driver, href):
    return get_elem_by_href_only(driver, href)
    
    
def get_link_elem_by_href(driver, lnk_obj):
    doc_xpath = "//a[@href='%s']" % lnk_obj.get('href', None)
    elem = driver.find_element_by_xpath(doc_xpath)
    return elem


DOWNLOAD_DIR = '/Users/rprasad/Downloads'
