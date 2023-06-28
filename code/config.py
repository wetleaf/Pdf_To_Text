# PDF path relative to working directory
PDF_path = "PDFs/dictionaries/Odia.Dictionary.pdf"
PDF_startpage = 7  # do not enter text page number (pdf page number should be given)
PDF_endpage   = 10

# Page Dir
PAGE_dir = "pages/"

# Word dir
WORD_dir = "words/"

# enable this if want to display word in WORD_dir
WORD_ENABLE = False

# Preprocessed Dir
PREPROCESSED_dir = "preprocessed/"

# enable this if want to display preprocessed image in PREPROCESSED_dir
PREPROCESSED_PAGE_ENABLE = True

# GAP allowed between two letters
GAP = 4

#overlap ratio allowed
OVERLAP_RATIO = 0.8

# Output file
OUTPUT_file = "output/Odia.Dictionary.txt"
#languages in pdf
LANGs = ["eng","ori"]

#Font Dictionary
FONT_dict = {
    "eng": ["fonts/Archivo Narrow_bold_italic.ttf",
            "fonts/Archivo Narrow_bold.ttf",
            "fonts/Archivo Narrow_italic.ttf",
            "fonts/Archivo Narrow.ttf",
            "fonts/arial.ttf",
            "fonts/Courier BOLD.ttf",
            "fonts/FontsFree-Net-SLC_.ttf"
    ],
    "ori": [
            "fonts/Lohit-Oriya.ttf"
    ]
}