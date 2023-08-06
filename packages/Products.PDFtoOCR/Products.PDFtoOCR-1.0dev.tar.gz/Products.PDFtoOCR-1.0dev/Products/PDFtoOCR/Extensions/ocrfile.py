def ocrfile(f, language=None):
    """ This method converts raw data of a pdf file to
        tiff images. Each pdf page gets converted to a tiff 
        image using ghostsscript.

        Using tesseract OCR is done on the images and finally
        the text is returned.
    """

    import urllib
    import os
    import sys
    import tempfile

    gs = '/usr/bin/gs'
    tess = '/usr/local/bin/tesseract'

    dir1 = tempfile.mkdtemp()
    pdffilename = dir1 + '/document.pdf'
    imagefilename = dir1 + '/image_%04d.tif'
    txtfilename = dir1 + '/output'
    txtoutput = ""

    file = open(pdffilename, "wb")
    file.write(f)
    file.close()
 
    # If the text is extractable with pdftotext don't
    # do ocr processing.
    # TODO: check somewhere in Plone is the pdftotext is done..
    pdftotext = os.popen2('pdftotext -enc UTF-8 %s -' % pdffilename)
    pdftext = pdftotext[1].read()
    if pdftext.strip():
        return None

    gsParams = [gs,
                '-dSAFER',
                '-dBATCH',
                '-dNOPAUSE',
                '-sDEVICE=tiffgray',
                '-r250',
                '-dTextAlphaBits=4',
                '-dGraphicsAlphaBits=4',
                '-dMaxStripSize=8192',
                '-sOutputFile=%s' % imagefilename,
                pdffilename,
                ]

    # Convert pdf to tiff images, each page is one tiff file
    os.spawnv(os.P_WAIT, gs, gsParams)
    os.remove(pdffilename)

    dirContents = os.listdir(dir1)
    dirContents.sort()

    # tesseract has other language abbrevations
    if language:
        tesseractLangs = {'de': 'deu',
                          'en': 'eng',
                          'fr': 'fra',
                          'it': 'ita',
                          'nl': 'nld',
                          'po': 'por'}
        language = tesseractLangs.get(language, 'eng')

    for image in dirContents:
        if image.startswith('image'):
            imagefilename = '%s/%s' % (dir1 , image)
             
            tessParams = [tess,
                          imagefilename,
                          txtfilename]
            if language:
                tessParams.append('-l')
                tessParams.append(language)

            # Do the OCR processing
            os.spawnv(os.P_WAIT, tess, tessParams)

            file = open(txtfilename + '.txt', "r")
            txtoutput += file.read()
            file.close()

            os.remove(txtfilename + '.txt')
            os.remove(imagefilename)

    # Clean-up temp dir
    os.rmdir(dir1)
    return txtoutput

if __name__ == '__main__':
    # stuff for testing this external method 
    file = open('/tmp/gasunie.pdf', "r")
    pdf =  file.read()
    output = ocrfile(None,pdf, 'deu')
    file.close()

    file = open('/tmp/output.txt', "wb")
    file.write(output)
    file.close()



