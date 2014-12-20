import os, sys
from rename_data2 import file_name_lu
import shutil

download_dir = 'downloads/2013_11_26'

def check_for_missing_files():
    lu_name_pdf = {}
    map(lambda key: lu_name_pdf.update({file_name_lu.get(key):key}), file_name_lu.keys() )

    sorted_keys = lu_name_pdf.keys()
    sorted_keys.sort()
    
    missing_cnt =0 
    cnt =0
    for pname in sorted_keys:
        cnt +=1
        pdf_name = lu_name_pdf.get(pname)
        fullname = os.path.join(download_dir, pdf_name)
        if os.path.isfile(fullname):
            pass
            #print '(%s) %s %s' % (cnt, pdf_name, pname)
        else:
            #print 'x >>(%s) %s %s' % (cnt, pdf_name, pname)
            print '\n(%s) %s\nfile should be:[%s]' % (cnt, pname.replace('-',', ').title(), pdf_name)
            missing_cnt +=1
    
    print 'total: %s' % cnt
    print 'missing: %s' % missing_cnt
    #print lu_name_pdf

def copy_rename_files():
    src_dir = 'downloads/2013_11_26'
    dest_dir = 'downloads/2013_11_26_renamed'
    
    cnt = 0
    for pdf_name, pname in file_name_lu.iteritems():
        src_file = os.path.join(src_dir, pdf_name)
        dest_file = os.path.join(dest_dir, '%s.pdf' % pname)
        if os.path.isfile(src_file):
            cnt +=1
            if os.path.isfile(dest_file):
                print '(%s:) done [%s]\n[%s]' % (cnt, src_file, dest_file)               
                continue
            shutil.copy2(src_file, dest_file)
            print '(%s) copy [%s]\n[%s]' % (cnt, src_file, dest_file)
            #if cnt == 2:
            #    break
    
def list_lu():
    cnt =0 
    for pdf_name, pname in file_name_lu.iteritems():
        cnt +=1
        print '(%s) %s %s' % (cnt, pdf_name, pname)
        
if __name__=='__main__':
    copy_rename_files()
    #check_for_missing_files()