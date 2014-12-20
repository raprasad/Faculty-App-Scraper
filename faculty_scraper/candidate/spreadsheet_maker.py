from django.db.models import Q
from django.template.defaultfilters import slugify
from datetime import datetime
import xlwt
from xlwt import easyxf

from common.msg_util import *
from common.xls_styles import *

from candidate.models import *
from settings import CANDIDATE_FINAL_DOCS

'''
python manage.py shell
from django.db.models import Q

from candidate.spreadsheet_maker import *
make_candidate_excel_file()

        
'''


def make_candidate_excel_file(candidate_ids=None):
    """From the Django admin view of a Person->Lab object, generate an Excel spreadsheet"""

    #candidates = Candidate.objects.all().order_by('lname', 'fname')
    if candidate_ids is None:
        candidates = Candidate.objects.all().order_by('lname', 'fname')
    else:
        candidates = Candidate.objects.filter(aries_id__in=candidate_ids).order_by('lname', 'fname')

    if candidates.count() == 0:
        msgx('Sorry!  No candidates found!')
    
    book = xlwt.Workbook(encoding="utf-8")
    # With a workbook object made we can now add some sheets.
    sheet1 = book.add_sheet('MCB candidates')

    date_obj = datetime.now()
    info_line = "Generated on %s" % (date_obj.strftime('%m/%d/%Y - %I:%M %p'))

    sheet1 = make_candidate_roster(sheet1, info_line, candidates)

    # create response object
    fname = 'mcb_candidates_%s.xls' % (date_obj.strftime('%m%d-%I-%M%p-%S').lower())
    fname = os.path.join(CANDIDATE_FINAL_DOCS, fname)
    
    # send .xls spreadsheet to response stream
    book.save(fname)
    msg('xls created: %s' % fname)
    

def get_max_len_attr(attr_name, lst_people, char_multiplier=256):
    # iterate through each attribute, turn it into a string, and then a len() integer
    '''for ln in lst_people:
        print ln.lname
        print unicode(ln.lname)
    '''
    attr_lengths = map(lambda x: len( unicode(x.__dict__.get(attr_name, ''))  ), lst_people)
    max_len = max( attr_lengths)

    if max_len < 10:
        return 10 * char_multiplier
    return max_len * char_multiplier



def make_candidate_roster(sheet1, info_line, people, **kwargs):
    """Spreadsheet for MCB Core admin use"""
    if sheet1 is None:
        return None
    if people is None:
        return sheet

    if info_line:
        sheet1.write(0, 0, info_line, style_info_cell)

    #   (header label, attribute, width)
    column_attributes = [ ('ARIES id', 'aries_id', 10)\
    , ('Last Name', 'lname', 20)\
    ,('First Name', 'fname', 20)\
    ,('Middle Initial', 'mi', 20)\
    ,('Email', 'email', 30)\
    ,('Phone', 'phone', 15)\
    ,('Title', 'title', 20)\
    ,('Institution', 'institution', 20)\
    \
    ,('Ph.D. Year', 'degree_date', 20)\
    ,('Ph.D. Institution', 'degree_institution', 20)\
    \
    ,('Recommender #1 Name', 'rec1', 30)
    ,('Rec #1 Received', 'rec1_position', 20)

    ,('Recommender #2 Name', 'rec2', 30)
    ,('Rec #2 Received', 'rec2_position', 20)

    ,('Recommender #3 Name', 'rec3', 30)
    ,('Rec #3 Received', 'rec3_position', 20)

    ,('Recommender #4 Name', 'rec4', 30)
    ,('Rec #4 Received', 'rec4_position', 20)

    ,('Recommender #5 Name', 'rec5', 30)
    ,('Rec #5 Received', 'rec5_position', 20)

    ]

    #----------------------------
    # Add the header row and set column widths
    #----------------------------
    char_multiplier = 256
    excel_row_num = 1
    for col_idx, (col_name, attr_name, col_width) in enumerate(column_attributes):
        sheet1.write(excel_row_num, col_idx, col_name, style_header)
        sheet1.col(col_idx).width = col_width * char_multiplier  

    #   Add data to the spreadsheet
    #
    for p in people:
        msgt('process: %s' % p)
        excel_row_num +=1

        for col_idx, (col_name, attr, col_width) in enumerate(column_attributes):

            if attr in ['degree_institution', 'rec2', 'rec3', 'rec4', 'rec5', 'rec1_position', 'rec2_position', 'rec3_position', 'rec4_position', 'rec5_position']:
                continue
            if attr == 'degree_date':
                degree_info = CandidateDegree.objects.filter(candidate=p)
                degree_info = degree_info.filter( Q(degree_type__in=['PhD', 'Ph.D.']) \
                        | Q(degree_type__istartswith='phd') \
                        | Q(degree_type__istartswith='ph.d') \
                        | Q(degree_type__istartswith='ph. d') \
                        | Q(degree_type__istartswith='doctor') \
                        | Q(degree_type__istartswith='dr rer nat') \
                        | Q(degree_type__istartswith='dphil') \
                        | Q(degree_type__icontains='(has MD but not PhD)') \
                    )
                print 'found: ', degree_info
                if degree_info.count()==1:
                    degree = degree_info[0]
                    if degree.degree_date:
                        phd_year = degree.degree_date
                    else:
                        phd_year = 'not entered'
                    sheet1.write(excel_row_num, col_idx, '%s' % phd_year, style_info_cell_wrap_on)
                    col_idx+=1
                    sheet1.write(excel_row_num, col_idx,'%s, %s' % (degree.degree_type, degree.institution), style_info_cell)
                    
                else:
                    msgx('Ph.D. degree not found!')
            elif attr == 'rec1':
                cnt = 0
                for rec in p.get_recommenders():
                    rec_parts = []
                    cnt += 1
                    if rec.prefix:
                        fullname = '%s %s' % (rec.prefix, rec.fullname)
                    else:
                        fullname = rec.fullname
                    rec_parts.append(fullname)

                    if rec.title: rec_parts.append(rec.title)
                    if rec.institution: rec_parts.append(rec.institution)
                    if rec.email: rec_parts.append(rec.email)
                    
                    rec_info = '\n'.join(rec_parts)
                    
                    sheet1.write(excel_row_num, col_idx, rec_info, style_info_cell_wrap_on)
                    col_idx+=1
                    
                    if rec.has_sent_recommendation():
                        sheet1.write(excel_row_num, col_idx, 'YES', style_info_cell_wrap_on)
                    else:
                        sheet1.write(excel_row_num, col_idx, 'NO', style_info_cell_wrap_on)
                        
                    col_idx+=1
                    
                while cnt < 5:
                    sheet1.write(excel_row_num, col_idx, '', style_info_cell); col_idx+=1
                    sheet1.write(excel_row_num, col_idx, '', style_info_cell); col_idx+=1
                    cnt+=1
                
                
                    
            else:
                # default for most attributes
                sheet1.write(excel_row_num, col_idx, unicode(p.__dict__.get(attr,  '')), style_info_cell_wrap_on)  
            col_idx+=1


    return sheet1



