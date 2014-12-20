import os, sys
from candidate.models import *

from common.msg_util import *
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import letter, A4 

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import *
from reportlab.lib.units import inch

class CandidateProfilePage:
    def __init__(self, candidate):
        self.candidate = candidate
        self.profile_filename = os.path.join(candidate.get_candidate_doc_path(),\
                                candidate.get_coversheet_filename())
        self.doc_elements = []
        
    def remove_profile_file(self):
        if os.path.isfile(self.profile_filename):
            os.remove(self.profile_filename)
            msg('Profile deleted: %s' % self.profile_filename)
    
    def add_paragraph(self, content, style_name='Normal'):
        if style_name=='Normal':
            content = ' &nbsp; &nbsp; &nbsp; %s' % content
        self.doc_elements.append( Paragraph(content, self.styles[style_name]))
        
        #elements.append(Paragraph("%s (aries id: %s) " % ( candidate.fname_lname().upper(), candidate.aries_id),\ styles['Heading2']))
                
    def build_profile(self):
        self.doc_elements = []
        self.styles = getSampleStyleSheet()
        
        c = self.candidate
        #------------------
        #self.add_paragraph("%s (aries id: %s) " % ( c.fname_lname().upper(), c.aries_id), 'Heading2')
        self.add_paragraph('%s' % c.fname_lname().upper(), 'Heading2')
        
        self.add_paragraph('Candidate Information', 'Heading3')
        
        
        #--------------------
        # Candidate Information
        #--------------------
        self.add_paragraph("<b>Name</b>: %s, %s %s " % (c.lname, c.fname, c.mi))
        if c.title:
            self.add_paragraph("<b>Title</b>: %s" % (c.title))
        else:
            self.add_paragraph("<b>Title</b>: (not given)")
        self.add_paragraph("<b>Institution</b>: %s" % (c.institution))
        self.add_paragraph('<b>Aries ID</b>: %s <a href="https://academicpositions.harvard.edu/hr/job_applications/%s"><u>view online</u></a>' % (c.aries_id, c.aries_id))
        #self.doc_elements.append(Spacer(1,0.2*inch))
        
        #--------------------
        # Contact Information
        #--------------------
        self.add_paragraph('Contact Information', 'Heading3')
        self.add_paragraph("<b>Email</b>: %s" % (c.email))
        self.add_paragraph("<b>Phone</b>: %s" % (c.phone))
        self.add_paragraph("<b>Address</b>: %s" % (c.addr1))
        if c.addr2: self.add_paragraph(" &nbsp;  &nbsp; &nbsp; %s" % (c.addr2))
        if c.addr3: self.add_paragraph(" &nbsp;  &nbsp; &nbsp; %s" % (c.addr3))
        if c.state: 
            self.add_paragraph(" &nbsp;  &nbsp; &nbsp; %s, %s %s" % (c.city, c.state, c.postal_code))
        elif not c.state: 
            self.add_paragraph(" &nbsp;  &nbsp; &nbsp; %s, %s" % (c.city, c.postal_code))
        self.add_paragraph("<b>Country</b>: %s" % (c.country))

        #self.doc_elements.append(Spacer(1,0.2*inch))

        #--------------------
        # Education
        #--------------------

        self.add_paragraph('Education', 'Heading3')
        degree_cnt = 0
        for idx, d in enumerate(c.get_degrees()):
            self.add_paragraph("<b>Degree</b>: %s, %s" % (d.degree_type, d.institution))
            #self.add_paragraph("%s focus: %s" % (d.degree_date, d.field_of_study))
            self.add_paragraph("<b>Degree Date</b>: %s" % (d.degree_date))
            self.add_paragraph("<b>Field of Study</b>: %s" % (d.field_of_study))

            #self.add_paragraph('%s, %s, %s' % (d.degree_type, d.institution, d.degree_date))
            #self.add_paragraph(' &nbsp; &nbsp; &nbsp; %s' % (d.field_of_study))
            self.doc_elements.append(Spacer(1,0.1*inch))
            degree_cnt+=1
        if degree_cnt == 0:
            self.add_paragraph("<i>(no education information)</i>")
            
        #--------------------
        # Recommendations
        #--------------------
        self.add_paragraph('Recommendations', 'Heading3')
        for r in c.get_recommenders():
            self.add_paragraph("<b>Name</b>: %s %s" % (r.prefix, r.fullname))
            self.add_paragraph("<b>Title/Institution</b>: %s / %s" % (r.title, r.institution))
            self.add_paragraph("<b>Email</b>: %s" % (r.email))
            self.add_paragraph("<b>Relation</b>: %s" % (r.relation))
            if r.has_sent_recommendation():
                self.add_paragraph("<b>Recommendation Sent</b>: YES")
            else:
                self.add_paragraph("<b>Recommendation Sent</b>: NO")
                
            self.doc_elements.append(Spacer(1,0.1*inch))

            
        #------------------
        # end of doc
        #--------------------
        self.add_paragraph("(end of cover sheet)", 'Heading4')
        
        
        self.remove_profile_file()  # remove older profile, if it exists
        
        pdf_doc_obj = SimpleDocTemplate(self.profile_filename)
        pdf_doc_obj.build(self.doc_elements)

        msg('saved: %s' % (self.profile_filename))
        #os.system('open %s' % self.profile_filename)
        
def make_candidate_profile_page(candidate):

    cpp = CandidateProfilePage(candidate)
    cpp.build_profile()
    

def delete_profiles():
    msgt('delete profiles!')
    cnt = 0
    for c in Candidate.objects.all():
        fout_name = os.path.join(c.get_candidate_doc_path(), c.get_coversheet_filename())
        if os.path.isfile(fout_name):
            cnt+=1
            os.remove(fout_name)
            msg('(%s) profile deleted: %s' % (cnt, fout_name))


def make_single_profile(aries_id):
    try:
        c = Candidate.objects.get(aries_id=aries_id)
    except Candidate.DoesNotExist:
        msg('Candiate not found for aries id: %s' % aries_id)
        return
    
    make_candidate_profile_page(c)    
    

def make_profile_files(max_cnt=1000, start_cnt=0):
    cnt =0
    profiles_made_cnt = 0
    for c in Candidate.objects.all():
        cnt+=1
        if cnt >= start_cnt:
            make_candidate_profile_page(c)
            profiles_made_cnt+=1

        if profiles_made_cnt >= max_cnt:
            msgx('done') 
            
