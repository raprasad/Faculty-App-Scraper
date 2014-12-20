"""
Download and rename the GCAST PDF Applications

"""

from selenium import webdriver
import time
from BeautifulSoup import BeautifulSoup# as Soup
import re, sys, os, shutil
from scrape_util_common import *
from datetime import datetime

#--------------------------
# NECESSARY ATTRIBUTES
#--------------------------
BASE_DOWNLOAD_DIR = '/Users/rprasad/mcb-git/Faculty-App-Scraper/gcast_scraping/downloads/'
NUM_APPLICATION_WEB_PAGES = 11   # number of web pages that list GCAST applicants (25 people per page)
#--------------------------
# end: necessary attributes
#--------------------------

TODAYS_DATE = datetime.today()
TODAYS_DATE_STR = TODAYS_DATE.strftime('%Y_%m%d')
GCAST_PDFS_DIR = os.path.join(BASE_DOWNLOAD_DIR, TODAYS_DATE_STR)
GCAST_PDFS_RENAMED_DIR = os.path.join(BASE_DOWNLOAD_DIR, '%s_renamed' % TODAYS_DATE_STR)


def pause(secs):
    msg('pausing for %s' % secs)
    time.sleep(secs)

class ApplicationScraper:
    
    GCAST_URL = 'https://asperin.fas.harvard.edu/Authenticator/login.do%s'\
                    % '?__authen_application=FAS_GSAS_GCAST'
    LOGIN_PAUSE_TIME_SECS = 12
    
    def __init__(self, download_dir, num_application_web_pages, name_match_list=None):

        self.download_dir = download_dir
        self.num_application_web_pages = num_application_web_pages
        self.name_match_list = name_match_list  # from a [] of names, attempt to pull specific applications

        self.applicant_id_name = {}
        self.applicant_dict_filename = os.path.join(self.download_dir, 'name_info.txt')  # to store the above {} in case script crashes

        self.browser = None
        
        self.set_the_firefox_webdriver()
        #self.download_applicant_files()
        #self.copy_rename_the_downloaded_files()
        
    def set_the_firefox_webdriver(self):
        # Set up the Firefox webdriver, including file download parameters
        
        # Start up the Firefox profile
        fp = webdriver.FirefoxProfile()

        # Set the download parameters in Firefox
        # When a PDF is clicked:
        #
        #   - Don't show the file dialog
        #   - Download the file to a specific directory
        #   - Disable Firefox's built-in PDF viewer
        #
        fp.set_preference("browser.download.dir", self.download_dir)
        fp.set_preference("browser.download.folderList",2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.helperApps.alwaysAsk.force", False)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf, text/xml, text/csv, text/plain, text/log, application/zlib, application/x-gzip, application/x-compressed, application/x-gtar, multipart/x-gzip, application/tgz, application/gnutar, application/x-tar, application/gzip")
        fp.set_preference("pdfjs.disabled", True)

        # Launch the webdriver browser and set it as a global variable
        self.browser = webdriver.Firefox(firefox_profile=fp)
                
        
    def download_applicant_files(self):
        # Start the process of downloading the appplicant files
        
        # (1) Go to the GCAST webpage
        self.browser.get(self.GCAST_URL)    

        # (2) Pause to allow PIN Login
        msgt('%s seconds to log in!!!!' % self.LOGIN_PAUSE_TIME_SECS)
        pause(self.LOGIN_PAUSE_TIME_SECS)

        #browser.switch_to_default_content()

        # (3) Click on to the "Review" tab
        msg('Click on the "Review" tab')
        elem = self.browser.find_element_by_id("levelonebutton7")
        elem.click()
        
        # (4) Iterate through the pages
        self.iterate_through_pages(self.browser, self.num_application_web_pages)

    def iterate_through_pages(self, browser, num_pages):

        for pg_num in range(1, num_pages+1):
            msgt('Downloading page: %s' % pg_num)
            page_link = 'https://asperin.fas.harvard.edu/gcast/protected/paging/filter-review-list.do?table_name=candidate_review_list&page_num=%s' % pg_num
            
            # use javascript to navigate to next page
            browser.execute_script('document.location="%s";return true;' % page_link)
            browser.switch_to_default_content()
            
            # download applications on this page
            self.download_application_pdfs(browser)

    def copy_rename_the_downloaded_files(self):
        global GCAST_PDFS_DIR, GCAST_PDFS_RENAMED_DIR, TODAYS_DATE_STR
        msgt('copy_rename_the_downloaded_files')
        src_dir = GCAST_PDFS_DIR
        dest_dir = GCAST_PDFS_RENAMED_DIR
        
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
            msg('directory created: %s' % dest_dir)

        if not os.path.isfile(self.applicant_dict_filename):
            msgx('name dict file not found: %s' % self.applicant_dict_filename)

        name_dict = eval(open(self.applicant_dict_filename, 'r').read())

        cnt = 0
        for pdf_name, pname in name_dict.iteritems():
            src_file = os.path.join(src_dir, pdf_name)
            dest_file = os.path.join(dest_dir, '%s-%s.pdf' % (pname, TODAYS_DATE_STR))
            if os.path.isfile(src_file):
                cnt +=1
                if os.path.isfile(dest_file):
                    print '(%s:) done [%s]\n[%s]' % (cnt, src_file, dest_file)               
                    continue
                shutil.copy2(src_file, dest_file)
                print '(%s) copy [%s]\n[%s]' % (cnt, src_file, dest_file)
            else:
                print 'source file not found'    
                
    def download_application_pdfs(self, browser):
        if browser is None:
            return
    
        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir)
            msg('directory created: %s' % self.download_dir)
        
        # Use beautiful soup to pull the applicant links
        #   For each applicant row:
        #       (1) Take the applicant name from the first column 
        #       (2) Pull the link to the PDF file from the second column
        #
        soup = BeautifulSoup(browser.page_source)    
        soup_table = soup.find(attrs={'class':'prettyTable'})

        cnt = 0
        # Iterate through the rows
        #
        for idx, soup_tr in enumerate(soup_table.findAll('tr')):
            if idx == 0:    # ignore header row
                continue
            for lnk_idx, soup_lnk in enumerate(soup_tr.findAll('a')):
                if lnk_idx == 0:    # Pull the name from the 1st column
                    name = soup_lnk.text        
                    name_lnk = soup_lnk.get('href', 'no name link')         
                    name_slug = poor_slugify(name)

                    print  '\n' + ('.' * 40)
                    print 'Name to match: %s' % name_slug
                    if self.name_match_list:        # Is there a name match list?
                        print 'match list exists'
                        if not name_slug in self.name_match_list: # If name doesn't match, go to next name
                            print 'no match'
                            break # get out of this loop (row)
                        print 'YES match'
                elif lnk_idx == 1:  # Pull the link from the 2nd column
                    pdf_link = soup_lnk.get('href',  None)
                    candidate_id = pdf_link[pdf_link.find('CANDIDATE_ID')+13:pdf_link.find('&RETURN_SCREEN')]
                    print 'candidate id: %s' % candidate_id
                    
                    # Download PDF
                    # Make mapping file
                    if pdf_link.find('candidate-pdf.do') > -1:
                        cnt +=1
                        
                        print  '\n' + ('-' * 40)
                        print '(%s) Download application for %s' % (cnt, name)
                        print '-' * 40
                        print pdf_link

                        candidate_fname = 'application_%s.pdf' % candidate_id
                        self.applicant_id_name.update({ candidate_fname : name_slug })
                        
                        open(self.applicant_dict_filename, 'w').write(str(self.applicant_id_name))
                        
                        pdf_fname_fullpath = os.path.join(self.download_dir, candidate_fname)
                        print 'check for file: %s' % pdf_fname_fullpath
                        if os.path.isfile(pdf_fname_fullpath):
                            print ':) file already downloaded'
                            continue

                        # Click the PDF Link!  And pause...
                        full_pdf_link = 'https://asperin.fas.harvard.edu%s' % pdf_link
                        browser.execute_script('document.location="%s";return true;' % full_pdf_link)
                        pause(self.LOGIN_PAUSE_TIME_SECS)
                        
                    # file download name
                    #orig_name = os.path.join(DOWNLOAD_DIR, 'viewapp.asp')
        
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

class NameMatchListMaker:
    """
    Given a list of names, format them as follows:
        - put in last name, first name order
        - slugify the name via "poor_slugify"
        - return names with an array []
    """
    @staticmethod
    def get_name_list(name_file):
        if not os.path.isfile(name_file):
            raise Exception('NameMatchListMaker. File does not exist: %s' % name_file)
       
        name_list = []
        for line in open(name_file, 'r').readlines():
            name_list.append(poor_slugify(u'%s' % line.strip()))

        return name_list
       
if __name__=='__main__':
    name_list = NameMatchListMaker.get_name_list('input/name_list_2014_0108.txt')
    print '\n'.join(name_list)

    scraper = ApplicationScraper(download_dir=GCAST_PDFS_DIR\
                                , num_application_web_pages=NUM_APPLICATION_WEB_PAGES\
                                , name_match_list=name_list)
    print scraper.applicant_id_name
    scraper.download_applicant_files()
    scraper.copy_rename_the_downloaded_files()
    
    #test_soup()
    #browser = webdriver.Firefox()
    #browser = webbrowser.Firefox() # Get local session of firefox
    #initiate(browser)
    #process_recommendations(browser)
