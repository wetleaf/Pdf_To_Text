from pdf2image import convert_from_path
import os
import shutil

def convert_pdf_into_pages(pdf_path,startpage,endpage,page_dir):

    # convert pdf to pages
    pages = convert_from_path(pdf_path)

    # remove the dir if exists
    if os.path.isdir(page_dir):
        shutil.rmtree(page_dir)
    
    # create a new dir
    os.mkdir(page_dir)

    # validate the endpage and startpage
    endpage = min(endpage,len(pages))
    startpage = max(1,startpage)

    # Get the pages in jpg
    for i in range(startpage-1,endpage):
        pages[i].save(os.path.join(page_dir,"page"+str(i+1)+".jpg"), 'JPEG')
        