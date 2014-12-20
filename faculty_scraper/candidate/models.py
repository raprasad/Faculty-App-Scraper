import os, shutil
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from settings import CANDIDATE_DOC_PATH, PDF_DOWNLOAD_DOC_PATH

class DocumentType(models.Model):
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )
        

class Candidate(models.Model):
    """Basic candidate info"""
    aries_id = models.IntegerField()
    #aries_username = models.CharField(max_length=100)
    prefix = models.CharField(max_length=20, blank=True)

    fname = models.CharField(max_length=70)
    mi = models.CharField(max_length=10, blank=True)
    lname = models.CharField(max_length=70)

    suffix = models.CharField(max_length=20, blank=True)

    title = models.CharField(max_length=100, blank=True)
    institution  =  models.CharField(max_length=100, blank=True)
    
    addr1 = models.CharField(max_length=70, blank=True)
    addr2 = models.CharField(max_length=70, blank=True)
    addr3 = models.CharField(max_length=70, blank=True)

    city = models.CharField(max_length=70, blank=True)
    state = models.CharField(max_length=70, blank=True)
    postal_code = models.CharField(max_length=25, blank=True)
    country = models.CharField(max_length=70, blank=True)

    phone = models.CharField(max_length=20, blank=True)

    email = models.EmailField()
    
    last_update = models.DateTimeField(auto_now=True)
    
    def get_coversheet_filename(self):
        fname = 'profile_cover_%s' % (self.aries_id)
        return slugify(fname) + '.pdf'
        
    def get_consolidated_pdf_filename(self):
        fname = '%s_%s_%s' % (self.lname, self.fname, self.aries_id)
        return slugify(fname) + '.pdf'
        
    def get_candidate_doc_path(self):
        """Return the candidate doc path--if it doesn't exist, create it"""
        
        doc_path = os.path.join(CANDIDATE_DOC_PATH, str(self.aries_id))
        if not os.path.isdir(doc_path):
            os.makedirs(doc_path)
        return doc_path 
        
    def get_degrees(self):
        return CandidateDegree.objects.filter(candidate=self)
    
    def get_blank_recommender_cnt_for_html(self):
        cnt = CandidateRecommender.objects.filter(candidate=self).count()
        if cnt >=5:
            return None
        missing_cnt = 5-cnt
        return range(1, missing_cnt+1)
    
    def get_recommenders(self):
        return CandidateRecommender.objects.filter(candidate=self)

    def get_phd_info(self):
        degree_info = CandidateDegree.objects.filter(candidate=self)
        degree_info = degree_info.filter( Q(degree_type__in=['PhD', 'Ph.D.']) \
                | Q(degree_type__istartswith='phd') \
                | Q(degree_type__istartswith='ph.d') \
                | Q(degree_type__istartswith='ph. d') \
                | Q(degree_type__istartswith='doctor') \
                | Q(degree_type__istartswith='dr rer nat') \
                | Q(degree_type__istartswith='dphil') \
                | Q(degree_type__icontains='(has MD but not PhD)') \
            )
        if degree_info.count()==1:
            return degree_info[0]
        return None    

    def has_required_docs(self):
        """
        Must have CandidateDocument with DocumentTypes with ids [1,2,3,4,5] 
        1 - CV, 2 - Cover Letter, etc.
        """
        ids = CandidateDocument.objects.filter(candidate=self, is_uploaded=True).values_list('doc_type__id', flat=True).order_by('doc_type__id')
        
        shared_ids = set(ids) & set([1, 2, 3, 4, 5])
        if list(shared_ids) == [1, 2, 3, 4, 5]:
            return True
        return False

    def get_uploaded_core_documents(self):
        return CandidateDocument.objects.filter(candidate=self, is_uploaded=True).order_by('doc_type__id')

    def get_uploaded_recommender_docs(self):
        return RecommenderDocument.objects.filter(candidate=self, is_uploaded=True).order_by('recommender_id')

    def aries_link(self):
        if not self.aries_id:
            return None
            
        return '<a href="https://academicpositions.harvard.edu/hr/job_applications/%s" target="aries_app">aries %s</a>' % (self.aries_id, self.aries_id) 
    aries_link.allow_tags = True 
    
    def recommendation_cnt(self):
        return RecommenderDocument.objects.filter(candidate=self).count()
        
    def __unicode__(self):
        return '%s, %s (aries: %s)'  % (self.lname, self.fname, self.aries_id)
        
    def fname_lname(self):
        name_parts = []
        if self.prefix: 
            name_parts.append(self.prefix)
            
        name_parts.append(self.fname)
        if self.mi: 
            name_parts.append(self.mi)
            
        name_parts.append(self.lname)

        name = ' '.join(name_parts)
            
        if self.suffix:
            name = name + ', %s' % self.suffix

        return name
        
    def get_address(self, delim='\n'):
        addr_lines = []
        for addr_line in [self.addr1, self.addr2, self.addr3]:
            if addr_line:
                addr_lines.append(addr_line)
        addr_lines.append('%s, %s %s' % (self.city, self.state, self.postal_code))        
        addr_lines.append(self.country)
        return delim.join(addr_lines)
    
    class Meta:
        ordering = ('lname', 'fname',)



    
class CandidateDegree(models.Model):
    candidate = models.ForeignKey(Candidate)
    degree_type = models.CharField(max_length=40)
    institution = models.CharField(max_length=100)
    degree_date = models.CharField(max_length=40, blank=True)
    field_of_study = models.CharField(max_length=100)

    class Meta:
        ordering = ('candidate',)

    def __unicode__(self):
        return '%s at %s for %s' % (self.degree_type, self.institution, self.candidate)

class CandidateRecommender(models.Model):
    candidate = models.ForeignKey(Candidate)
    
    prefix = models.CharField(max_length=20, blank=True)
    fullname = models.CharField(max_length=100)
    
    title = models.CharField(max_length=100, blank=True)
    institution  =  models.CharField(max_length=100, blank=True)
    
    email = models.EmailField()
    
    relation = models.CharField('How do you know this reference?', max_length=255, blank=True)
    
    def __unicode__(self):
        return '%s for %s' % (self.fullname, self.candidate)

    class Meta:
        ordering = ('candidate',)

    def get_lname(self, fullname):
        name_parts = fullname.split(',')    # take off any ', M.D.' ,etc
        lname = name_parts[0].split()[-1].lower().strip()
        return lname

    def has_sent_recommendation(self):
        crec = self
        l = RefereeForm.objects.filter(candidate=crec.candidate)
        for rf in l:
            #print 'RefereeForm: %s - %s' % (rf.id, rf)
            # full name match
            if crec.fullname.lower().strip()== rf.fullname.lower().strip():
                #print 'fullname match!'
                return True
        for rf in l:        
            # email match
            if crec.email and rf.email:
                if crec.email.lower().strip()== rf.email.lower().strip():
                    #print 'email match!'
                    return True
        for rf in l:
            # last name match
            if not rf.fullname:
                print 'referee form deleted: %s' % rf
                rf.delete()
            else:
                #print 'check last name'
                lname1 = self.get_lname(crec.fullname)
                lname2 = self.get_lname(rf.fullname)
                if lname1 == lname2:
                    return True
        return False

class CandidateDocument(models.Model):
    candidate = models.ForeignKey(Candidate)
    doc_type = models.ForeignKey(DocumentType)
    doc_name = models.CharField(max_length=255)
    doc_fullpath = models.CharField(max_length=255, blank=True, help_text='auto-save on fill')
    is_uploaded = models.BooleanField(default=False)

    last_update = models.DateTimeField(auto_now_add=True)

    def does_doc_exist(self):
        if os.path.isfile(self.doc_fullpath):
            self.is_uploaded = True
            self.save()
            return True
        return False

    def mark_to_delete_in_download_folder(self):
        orig = os.path.join(PDF_DOWNLOAD_DOC_PATH, self.doc_name)
        if os.path.isfile(orig):
            print orig
            xout = os.path.join(PDF_DOWNLOAD_DOC_PATH, 'x_%s' % self.doc_name)
            shutil.move(orig, xout)
            print 'moved to: %s' % xout


    def move_from_download_to_candidate_dir(self):
        orig = os.path.join(PDF_DOWNLOAD_DOC_PATH, self.doc_name)
        if os.path.isfile(orig):
            print orig
            if not self.doc_fullpath:
                self.set_doc_fullpath()
            shutil.move(orig, self.doc_fullpath)
            self.is_uploaded = True
            self.save()
            print 'moved to: %s' % self.doc_fullpath

    def __unicode__(self):
        return '%s - %s for %s, %s' % (self.doc_name, self.doc_type, self.candidate.lname, self.candidate.fname)
    
    def set_doc_fullpath(self):
        self.doc_fullpath = os.path.join(self.candidate.get_candidate_doc_path()\
                                    , self.doc_name)
        
    def save(self):
        self.set_doc_fullpath()
        super(CandidateDocument, self).save()
        
    class Meta:
        ordering = ['candidate', 'doc_type__id', 'doc_name']
"""
from candidate.models import *
l = CandidateDocument.objects.all()
for f in l: print f.does_doc_exist()
for f in l: f.move_from_download_to_candidate_dir()

"""

class RefereeForm(models.Model):
    candidate = models.ForeignKey(Candidate)
    recommender_id = models.IntegerField()
    fullname = models.CharField(max_length=100)
    institution  =  models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)

    def __unicode__(self):
        return '%s for %s' % (self.fullname, self.candidate)

    class Meta:
        ordering = ('candidate', 'recommender_id',)


class RecommenderDocument(models.Model):
    """No obvious way to connect the recommender to a document"""
    candidate = models.ForeignKey(Candidate)
    recommender_id = models.IntegerField()
    doc_name = models.CharField(max_length=255)
    doc_fullpath = models.CharField(max_length=255, blank=True)
    is_uploaded = models.BooleanField(default=False)

    last_update = models.DateTimeField(auto_now_add=True)
    
    def set_doc_fullpath(self):
        self.doc_fullpath = os.path.join(self.candidate.get_candidate_doc_path()\
                                    , str(self.recommender_id)
                                    , self.doc_name)    
                                    
    def save(self):
        self.set_doc_fullpath()
        super(RecommenderDocument, self).save()
    
    def does_doc_exist(self):
        if os.path.isfile(self.doc_fullpath):
            self.is_uploaded = True
            self.save()
            return True
        return False

    def __unicode__(self):
        return '%s for %s, %s' % (self.doc_name, self.candidate.lname, self.candidate.fname)
    

"""

from candidate.models import *
import sys
def has_sent_recommendation(crec):
    l = RefereeForm.objects.filter(candidate=crec.candidate)
    for rf in l:
        print 'RefereeForm: %s' % rf.id
        # full name match
        if crec.fullname.lower().strip()== rf.fullname.lower().strip():
            return True
        # email match
        if crec.email and rf.email:
            if crec.email.lower().strip()== rf.email.lower().strip():
                return True
        # last name match
        if not rf.fullname:
            print 'NO NAME in RefereeForm: %s' % rf.id
            print 'NO NAME in RefereeForm: %s' % rf
            sys.exit(0)
        else:
            lname1 = crec.fullname.split()[0].lower().strip()
            lname2 = rf.fullname.split()[0].lower().strip()
            if lname1 == lname2:
                return True
    return False

total =0
fnd =0 
for crec in CandidateRecommender.objects.all():
    print '-' * 40
    print crec
    total+=1
    if has_sent_recommendation(crec): 
        fnd+=1    
    print 'found: %s/%s' % (fnd, total)

"""    
