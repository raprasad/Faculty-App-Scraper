from django.template.loader import render_to_string
from settings import CANDIDATE_FINAL_DOCS
from candidate.models import Candidate
from common.msg_util import *
import os

def make_candidate_listing_page(candidate_ids=None):

    if candidate_ids is None:
        candidates = Candidate.objects.all().order_by('lname', 'fname')
    else:
        candidates = Candidate.objects.filter(aries_id__in=candidate_ids).order_by('lname', 'fname')


    if candidates.count() == 0:
        msgx('Sorry!  No candidates found!')

    content = render_to_string('candidate_listing.html', { 'candidates': candidates})
    fname = os.path.join(CANDIDATE_FINAL_DOCS, 'candidate_listing.html')
    fh = open(fname, 'w')
    fh.write(content.encode('utf-8'))
    fh.close()
    msgt('file written: %s' % fname)
    