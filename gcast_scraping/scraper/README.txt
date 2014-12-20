#----------------------------------
Purpose: Download PDF-format Graduate Student applications from GCAST 
#----------------------------------

Tools: 
    - python 2.7
    - selenium: http://www.seleniumhq.org/
    - beautiful soup: http://www.crummy.com/software/BeautifulSoup/
    
Process:
    - Use Selenium to drive Firefox and open the GCAST page, pausing for entry of HUID
    - Navigate to the list of applications
    - "Click" on each application to downloading the PDF file
        - The PDF file is named by applicant #
        - In memory, store a python dict { PDF file name : applicant name } 
    - Use the python dict to rename the PDF files to the applicant names (lname_fname)
    
Usage:
    - Edit gcast_scraper.py, fill in attributes at the top
    - python gcast_scraper.py

Notes:
    - works as of 11/26/2013