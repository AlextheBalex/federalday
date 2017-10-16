# script to download all "Plenardebatten" from the Deutscher Bundestag

# http://dipbt.bundestag.de/doc/btp/17/17140.pdf

from os import listdir

base_url = "http://dipbt.bundestag.de/doc/btp/"

def get_name( period, docnum ):
    return base_url + '{:=02}'.format(period) + "/" + '{:=02}'.format(period) + '{:=03}'.format(docnum) + ".pdf"
    
    
def download(url):
    """Copy the contents of a file from a given URL
    to a local file.
    """
    import urllib2
    import os.path
    print "fetching " + url
    
    # get url
    
    try: 
        webFile = urllib2.urlopen(url)
    except urllib2.HTTPError:
        print "failed"
        return False
        
    if webFile.getcode() != 200:
        return False
    if webFile.geturl().find("navigation") != -1:
        return False
    
    # filename & dir
    local_name = "/home/foritisiemperor/Music/transform_pdf/app/pdfs/plenarprotokolle/" + url.split(base_url)[-1]
    local_dir = local_name[:-9]
    print local_name, 9
    if os.path.exists(local_dir) == False:
        if os.makedirs(local_dir) == False:
            print "failed creating dir " + local_name
            return False
    
    # save
    localFile = open(local_name, 'w')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()
    return True


def get_last_pdf_legnum_docnum():
    file_path = '/home/foritisiemperor/Music/transform_pdf/app/pdfs/plenarprotokolle/'
    l_directories = listdir(file_path)
    try:
        latest_leg_period = int(sorted(l_directories)[-1])
    except IndexError:
        return 1, 1
    
    l_files_latest_leg_period = listdir('/'.join([file_path, str(latest_leg_period)]))
    try:
        latest_document = sorted(l_files_latest_leg_period)[-1]
        docnum = int(str(latest_document)[2:-4])
        return latest_leg_period, docnum
    except IndexError:
        return latest_leg_period, 1
    
# print get_last_pdf_docnum()
    

def download_latest_plenarprotokolle():
    latest_leg_period, latest_docnum = get_last_pdf_legnum_docnum()
    new_documents = False
    for period in xrange(latest_leg_period, 20):
        
        start = latest_docnum + 1
        #if period == 1: start = 4683
        
        for docnum in xrange(start, 999):
            if download(get_name(period, docnum)) == False:
                print "failed"
                break
            else:
                new_documents = True
    return new_documents
# download_latest_plenarprotokolle()
