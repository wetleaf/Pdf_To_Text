import config
import pdftopages
import preprocess
import ocr
import postprocess

# generate pages from pdf
pdftopages.convert_pdf_into_pages(config.PDF_path,config.PDF_startpage,config.PDF_endpage,config.PAGE_dir)

# write lines in the text file
file = open(config.OUTPUT_file,"w")

# get the words at page number
pre = preprocess.Preprocess(config.PAGE_dir,config.WORD_dir,config.PREPROCESSED_dir,config.GAP,config.OVERLAP_RATIO,config.WORD_ENABLE,config.PREPROCESSED_PAGE_ENABLE)

for pagenum in range(config.PDF_startpage,config.PDF_endpage+1):
    print("Processing page {}".format(pagenum))
    file.write("Page "+str(pagenum) + "\n")
    words = pre[pagenum] # word is list of [img,box]

    # get the text at that page number
    text_genorator = ocr.OCR(words,config.LANGs,config.FONT_dict)
    texts = text_genorator.image_to_text()  # text is list([[text,lang],box])

    # postprocess
    pos = postprocess.PostProcess(pre.img.shape[:2])
    lines = pos.arrange_in_line(texts,pre.horizontal_lines,pre.vertical_lines)

    # write each line in the file
    for line in lines:

        for word in line:
            text = word[0][0]
            file.write(text+" ")
        file.write('\n')
    
    file.write('\n')
print("Processing Finished!!")

file.close()
