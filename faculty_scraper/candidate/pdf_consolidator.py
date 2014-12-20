import os, sys
from candidate.models import *

from settings import CANDIDATE_FINAL_DOCS
from common.msg_util import *
import commands # unix only

"""
python '/System/Library/Automator/Combine PDF Pages.action/Contents/Resources/join.py' -o './test_out.pdf' './pdf/contact.pdf' './pdf/flip4.pdf'

"""

"""
(1) pull pdf file names into { }
(2) order files names
(3) construct combine statement
(4) combine
"""

def make_single_pdf(candidate):  

    msg('Make PDF for %s' % candidate)
    # collect the document names into a list
    
    if not candidate.has_required_docs():
        for doc in candidate.get_uploaded_core_documents():
            print doc.doc_type, doc.doc_type.id, doc
        msgx('Does not have all required documents')
        
    cover_sheet = os.path.join(candidate.get_candidate_doc_path()\
                                , candidate.get_coversheet_filename())
    if not os.path.isfile(cover_sheet):
        msgx('cover sheet missing: %s' % cover_sheet)

    # ADD cover sheet
    pdf_fnames = [cover_sheet]                  
    # ADD candidate submitted docs
    for doc in candidate.get_uploaded_core_documents():
        pdf_fnames.append(doc.doc_fullpath)     

    # ADD recommendations
    for rec_doc in candidate.get_uploaded_recommender_docs():
        pdf_fnames.append(rec_doc.doc_fullpath)
            
    # get consolidated PDF name
    fout_name = os.path.join(CANDIDATE_FINAL_DOCS, 'pdfs',  candidate.get_consolidated_pdf_filename())
    if os.path.isfile(fout_name):
        os.remove(fout_name)
        print 'removed old consolidated PDF'

    # construct a command to combine the files--use OS X's Automator script
    #
    pdf_stmt = """/usr/bin/python '/System/Library/Automator/Combine PDF Pages.action/Contents/Resources/join.py' --verbose -o  '%s' %s""" % (fout_name, ' '.join(pdf_fnames))

    msg(pdf_stmt)
    msgt('making pdf. target output file: [%s]' % fout_name)
    msg(commands.getoutput(pdf_stmt))
    
    # open file
    #os.system('open %s' % fout_name)


def make_pdf_files(max_cnt=1000, start_cnt=0):
    cnt =0
    pdfs_made_cnt = 0
    for c in Candidate.objects.all():
        cnt+=1
        if cnt >= start_cnt:
            msgt('(%s) Make PDF for %s' % (cnt, c))
            
            make_single_pdf(c)
            pdfs_made_cnt+=1

        if pdfs_made_cnt >= max_cnt:
            msgx('done')
   

def make_single_pdf_with_id(aries_id):
    try:
        c = Candidate.objects.get(aries_id=aries_id)
    except Candidate.DoesNotExist:
        msg('Candiate not found for aries id: %s' % aries_id)
        return

    make_single_pdf(c)    

    
    
    
    
    
    
