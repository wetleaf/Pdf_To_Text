# **PDF_TO_TEXT**
This program converts the pdf consisting of multiple languages into equivalent text using **Tesseract OCR**.

## **Installation**
1. Clone the github repositery

    ```
    git clone https://github.com/wetleaf/pdf_to_text.git
    ```

2. Install the requirements
    ```
    pip install -r requirements.txt
    ```
3. Download the traindata of language you want to parse. For example eng,ori etc.
    ```
    wget https://github.com/tesseract-ocr/tessdata/raw/main/ori.traineddata -O [directory you want]/tessdata

    wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata -O [directory you want]/tessdata


    ```
4. Export the TESSDATA_PREFIX with the file tessdata
    ```
    export TESSDATA_PREFIX=[directory]/tessdata
    ```
5. Download (.ttf files) the fonts of language that pdf contains (*most similar* most to the pdf produce *more accuracy*) into **fonts/** directory. 

## **How to Run**

1. Update the **code/config.py**

    1. **PDF_path**:- path to the pdf file to parse
    2. **PDF_startpage**:- starting page from which parsing should be started (>0)
    3. **PDF_endpage**:- ending page till which parsing should be done (included) 
    4. **PAGE_dir**:- pages converted into image are saved to PAGE_dir directory
    5. **WORD_dir**:- words segmented from pages are saved in WORD_dir directory (can avoid this by updating parameter **WORD_ENABLE** in config file)
    6. **PREPROCESSED_dir**:- preprocessed page are saved in PREPROCESSED_dir (can avoid this by updating parameter **PREPROCESSED_PAGE_ENABLE** in config file)
    7. **OUTPUT_file**:- Name of output file in which parsed text will be written
    8. **LANGs**:- list of languages invloved in pdf **(make sure to enter 3 letter code of language, do check https://github.com/tesseract-ocr/tessdata to get the letter code)**
    9. **FONT_dict**:- Make a dictionary of languages-fonts used. Example:
        ```
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
        ```
    10. **GAP**:- gap allowed between the letters (should not be to large so it capture multiple word nor too low so it capture letters instead of word) (Default 4)
    11. **OVERLAP_RATIO**:- Ratio to eliminate overlapping boxes (Default 0.8)
2. Run the main file
    ```
    python code/main.py
    ```

## **Problem:**
1. Tesseract convert the image into text well in *word segemented level*.
2. Tesseract requires *language of the image word* to get the text.
3. Task is to *find the language* of the given word image. Example, *words/* dir

## **Solution:**
1. Say L1, L2, L3 ... Ln are possible languages and I is the word image
2. Use tesseract to convert image I in all of the above language one by one. Say X1 = L1(I), X2 = L2(I) and so on.
3. Now reverse back and produce image of same dimension of text X1, X2 .... Xn using PIL in different fonts of above languages. Lets call this images I1,I2,I3....In
4. compare I with I1, I2, I3,... In and output the image with most similar text. (used SSIM for this model)
5. This gives text as well as correct language 

**Note:** model depends on font provided. More similar fonts produce more accurate text

## **Hacks**
To improve the accuracy some hacks can be used. For example
    
1. Converting an word image of language L1 into other language L2 produce text which are not in unicode range of L2 . It can be identified and used to validate the language prediction. (This hack is implemented in https://github.com/wetleaf/OdiaToEnglish to parse odia dictionary.)
2. If pdf follow some structure like [L1] [L2].. so on. Then we can use this structure to get the language of words
3. For Dictionaries, every line first word are in ascending order. We can use this fact to validate the text


