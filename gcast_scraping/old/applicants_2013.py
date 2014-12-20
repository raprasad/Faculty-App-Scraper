from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
#from BeautifulSoup import BeautifulSoup as Soup
#import re, sys, os, shutil
#from scrape_util_common import *
from datetime import datetime

browser = webdriver.Firefox()
browser.get('https://asperin.fas.harvard.edu/Authenticator/login.do?__authen_application=FAS_GSAS_GCAST')
print 'please log in for (10 second delay)'
time.sleep(10)
element = browser.find_element_by_id("levelonebutton7")
element.click()
tbl = browser.find_element_by_class_name("prettyTable")

#https://asperin.fas.harvard.edu/gcast/protected/candidate-pdf.do?COLLABORATION_LEVEL_NAME=COL_LEV_REV&APPLICATION_ID=2010565&CANDIDATE_ID=2010565&RETURN_SCREEN=review.search.screen
# Iterate through rows - each row is an applicant
#
row_cnt = 0
candidate_name = None
candidate_pdf_link = None
for table_row_element in tbl.find_elements_by_tag_name("tr"):
    row_cnt +=1
    if row_cnt == 3: continue       # skip first 3 rows
    table_columns = table_row_element.find_elements_by_tag_name('td')   # pull columns
    candidate_name_tag = table_columns[0].find_element_by_tag_name("a")
    candidate_name = candidate_name_tag.text    # get name from 1st col
    print candidate_name
    #
    candidate_pdf_link = table_columns[1].get_attribute('href') # get PDF link from 2nd col
    
    print '(%s) %s' % (row_cnt, candidate_name)
    
    for tbl_column in table_row_element.find_elements_by_tag_name('td'):     # go to the first <td>

        col_cnt +=1
        if col_cnt > 2: continue    # skip co
            break
        link_element = tbl_column.find_element_by_tag_name("a") 
        if col_cnt==1:
            candidate_name = link_element.text         # pull the name from the link
        elif col_cnt == 2:
            candidate_pdf_link = link_element.get_attribute('href')    # pull the link to 
            print candidate_name#, candidate_pdf_link

    print '-' * 40
    print candidate_name#, candidate_link
