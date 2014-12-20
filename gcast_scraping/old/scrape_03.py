from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from BeautifulSoup import BeautifulSoup as Soup
import re, sys, os, shutil
from scrape_util_common import *
from datetime import datetime

"""


fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList",2)
fp.set_preference("browser.download.manager.showWhenStarting",False)

download_dir = os.path.join('/Users/rprasad/mcb-git/Faculty-App-Scraper/gcast_scraping/test')
fp.set_preference("browser.download.dir", download_dir)
#fp.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")
fp.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")
fp.set_preference("browser.helperApps.neverAsk.saveToDisk","binary")
browser = webdriver.Firefox(firefox_profile=fp)

#browser = webdriver.Firefox()

#browser = webdriver.Chrome()

browser.get('https://asperin.fas.harvard.edu/Authenticator/login.do?__authen_application=FAS_GSAS_GCAST')

elem = get_link_elem_by_href_text(browser, '/gcast/protected/filter-review-list.do')
elem.click()

pg_num = 1
page_link = 'https://asperin.fas.harvard.edu/gcast/protected/paging/filter-review-list.do?table_name=candidate_review_list&page_num=%s' % pg_num

browser.execute_script('document.location="%s";return true;' % page_link)

soup = Soup(browser.page_source)    
soup_table = soup.find(attrs={'class':'prettyTable'})


cnt = 0
for idx, soup_tr in enumerate(soup_table.findAll('tr')):
    if idx == 0:    # ignore header row
        continue
    for lnk_idx, soup_lnk in enumerate(soup_tr.findAll('a')):
        if lnk_idx == 0:
            name = soup_lnk.text        
            name_lnk = soup_lnk.get('href', 'no name link')         
            name_slug = poor_slugify(name)
        elif lnk_idx == 1:
            pdf_link = soup_lnk.get('href', 'no pdf link')
            candidate_id = pdf_link[pdf_link.find('CANDIDATE_ID')+13:pdf_link.find('&RETURN_SCREEN')]
            
            
            # Download PDF
            if pdf_link.find('candidate-pdf.do'):
                cnt +=1
                print '(%s) Download application for %s' % (cnt, name)
                print pdf_link
    
                full_pdf_link = 'https://asperin.fas.harvard.edu%s' % pdf_link
                browser.execute_script('document.location="%s";return true;' % full_pdf_link)
                print 'pause for download'            
                pause(12)
"""
def pause(secs):
    msg('pausing for %s' % secs)
    time.sleep(secs)

class ApplicationScraper:
    def __init__(self, download_dir='downloads'):

        self.download_dir = download_dir
        #os.path.join(download_dir, datetime.now().strftime('%Y_%m_%d'))
        self.applicant_id_name = {}
        # set firefox download parameters
        fp = webdriver.FirefoxProfile()
        #fp = webdriver.Chrome()
        
        fp.set_preference("browser.download.dir", self.download_dir)
        fp.set_preference("browser.download.folderList",2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.helperApps.alwaysAsk.force", False)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf, text/xml, text/csv, text/plain, text/log, application/zlib, application/x-gzip, application/x-compressed, application/x-gtar, multipart/x-gzip, application/tgz, application/gnutar, application/x-tar, application/gzip")
        fp.set_preference("pdfjs.disabled", True)
        #fp.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")
        #fp.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")

        self.browser = webdriver.Firefox(firefox_profile=fp)
                
        self.initiate()
        
    def initiate(self):

        self.browser.get('https://asperin.fas.harvard.edu/Authenticator/login.do%s'\
                        % '?__authen_application=FAS_GSAS_GCAST')
        #browser.get("https://asperin.fas.harvard.edu/gcast/") # Load page
        msgt('15 seconds to log in!!!!')
        pause(15)

        #browser.switch_to_default_content()

        # go to the "Review" tab
        elem = get_link_elem_by_href_text(self.browser, '/gcast/protected/filter-review-list.do')
        elem.click()
    
        msgt('MAKE SURE TO DOWNLOAD 1 FILE TO GET IT STARTED')
        #pause(20)
    
        self.iterate_through_pages(self.browser)

    def iterate_through_pages(self, browser, num_pages=3):

        for pg_num in range(1, num_pages+1):
            msgt('Downloading page: %s' % pg_num)
            page_link = 'https://asperin.fas.harvard.edu/gcast/protected/paging/filter-review-list.do?table_name=candidate_review_list&page_num=%s' % pg_num
            browser.execute_script('document.location="%s";return true;' % page_link)
            browser.switch_to_default_content()
            self.download_application_pdfs(browser)


    def download_application_pdfs(self, browser):
        if browser is None:
            return
    
        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir)
            msg('directory created: %s' % self.download_dir)
        
        soup = Soup(browser.page_source)    
        soup_table = soup.find(attrs={'class':'prettyTable'})
        print dir(soup_table)
        cnt = 0
        for idx, soup_tr in enumerate(soup_table.findAll('tr')):
            if idx == 0:    # ignore header row
                continue
            for lnk_idx, soup_lnk in enumerate(soup_tr.findAll('a')):
                if lnk_idx == 0:
                    name = soup_lnk.text        
                    name_lnk = soup_lnk.get('href', 'no name link')         
                    name_slug = poor_slugify(name)
                elif lnk_idx == 1:
                    pdf_link = soup_lnk.get('href',  None)
                    candidate_id = pdf_link[pdf_link.find('CANDIDATE_ID')+13:pdf_link.find('&RETURN_SCREEN')]
                    print 'candidate id: %s' % candidate_id
                    
                    # xDownload PDF
                    # Make mapping file; name to application id
                    if pdf_link.find('candidate-pdf.do') > -1:
                        cnt +=1
                        
                        print  '\n' + ('-' * 40)
                        print '(%s) Download application for %s' % (cnt, name)
                        print '-' * 40
                        print pdf_link

                        candidate_fname = 'application_%s.pdf' % candidate_id
                        self.applicant_id_name.update({ candidate_fname : name_slug })
                        print 'check for file: %s' % candidate_fname
                        print 'in directory: %s' % self.download_dir
                        if os.path.isfile(os.path.join(self.download_dir, candidate_fname)):
                            print 'file already downloaded'
                            continue
            
                        full_pdf_link = 'https://asperin.fas.harvard.edu%s' % pdf_link
                        browser.execute_script('document.location="%s";return true;' % full_pdf_link)
                        pause(15)
                    # file download name
                    orig_name = os.path.join(DOWNLOAD_DIR, 'viewapp.asp')
        
                    # clear the previous download if it didn't happen yet
                    """
                    if os.path.isfile(orig_name):
                        os.remove(orig_name)
                        FAILED_NAMES.append(orig_name)
                        print 'cleaned bad file'
                        pause(1)
            
                    pdf_name = '%s_%s.pdf' % (lname.text.upper(), fname.text.lower()) 
                    print pdf_name
        """

       
if __name__=='__main__':
    scraper = ApplicationScraper(download_dir='/Users/rprasad/mcb-git/Faculty-App-Scraper/gcast_scraping/downloads/2013_11_26')
    print scraper.applicant_id_name
    
    #test_soup()
    #browser = webdriver.Firefox()
    #browser = webbrowser.Firefox() # Get local session of firefox
    #initiate(browser)
    #process_recommendations(browser)
