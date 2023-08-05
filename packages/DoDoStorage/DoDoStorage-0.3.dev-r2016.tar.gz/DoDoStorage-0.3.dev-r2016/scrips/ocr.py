# very dirty bach OCR engine

import os, re, time, shutil, sys

starttime = time.time()
success = 0
failure = 0

def ocr(inputfile, dontrotate=False):
   """Try to extract Vorgangsnummer et al via ocr from inputfile. On success move file
      info files/ocr-success/AUFTRAGSNUMMER-VORGANGSNUMMER-TIMESTAMP.png
      else move it into files/ocr-failure/"""

   global success, failure

   fd = os.popen('hocr=0 spell=0 verbose=0 /root/ocropus/ocropus-cmd/ocropus ocr %s' % inputfile, 'r')
   textdata = fd.read()
   print len(textdata)

   ocrdict = {}
   m = re.compile(r'Datu[mn] (?P<belegdatum>[ 123]?\d\.[01]\d\.[01]\d)?', re.M).search(textdata)
   if m:
       ocrdict.update(m.groupdict())
   m = re.compile(r'Termin (?P<lieferdatum>[ 123]?\d\.[01]\d\.[01]\d)?', re.M).search(textdata)
   if m:
       ocrdict.update(m.groupdict())
   m = re.compile(r'Vorgang (?P<vorgangsnummer>\d\d\d\d\d\d\d\d)?', re.M).search(textdata)
   if m:
       ocrdict.update(m.groupdict())
   m = re.compile(r'((Aus|Um)\s?lagerung aus (?P<bewegungsart>.*))', re.M).search(textdata)
   if m:
       ocrdict.update(m.groupdict())
   m = re.compile(r'Auftr-Nr (?P<auftragsnummer>\d\d\d\d\d\d)', re.M).search(textdata)
   if m:
       ocrdict.update(m.groupdict())
   m = re.compile(r'(?P<ende>\*\* Ende der Liste \*\*)', re.M).search(textdata)
   if m:  
       ocrdict.update(m.groupdict())

   print ocrdict
   if ocrdict.get('ende') == '** Ende der Liste **' and 'auftragsnummer' in ocrdict \
     and 'vorgangsnummer' in ocrdict and 'belegdatum' in ocrdict:
       # assume it workred
       newfilename = '%d-%d-%d.png' % (int(ocrdict['auftragsnummer']), int(ocrdict['vorgangsnummer']), time.time())
       shutil.move(inputfile, os.path.join('./files/ocr-success', newfilename))
       print "moved to", os.path.join('./files/ocr-success', newfilename)
       success += 1
   else:
       newfilename = 'failed-%d.png' % time.time()
       shutil.move(inputfile, os.path.join('./files/ocr-failure', newfilename))
       print "moved to", os.path.join('./files/ocr-failure', newfilename)
       if dontrotate:
           failure += 1
       else:    
           print "rotating"
           os.system('gm convert -rotate 180 %s %s' % (os.path.join('./files/ocr-failure', newfilename), inputfile))
           ocr(inputfile, dontrotate=True)

def handle_file(inputfile):
    """Move and convert a file arround until it is ready for OCR"""

    shutil.move(inputfile, os.path.join('./files/ocring/', '%05d-%s' % (os.getpid(), os.path.basename(inputfile))))
    inputfile = os.path.join('./files/ocring/', '%05d-%s' % (os.getpid(), os.path.basename(inputfile)))
    print 'converting %s %s' % (inputfile, inputfile + '.png')
    if os.system('gm convert %s %s' % (inputfile, inputfile + '.png')):
        print "gm convert error"
        sys.exit(1)
    if not os.path.exists(inputfile + '.png'):
        print inputfile + '.png', 'is missing'
        sys.exit(1)
    os.unlink(inputfile)
    inputfile = inputfile + '.png'
    print "inputfile = %s" % inputfile
    ocr(inputfile)

while 1:
    empty_run = True
    for root, dirs, files in os.walk('./files/scanned/'):
        print root
        for filepath in [os.path.join(root, name) for name in files]:
            if os.path.exists(filepath) and (filepath.endswith('.pnm') or filepath.endswith('.png')):
                print "found", filepath
                handle_file(filepath)
                empty_run = False
            else:
               print "unwanted file", filepath
            print "******************************************************"
            delta = time.time() - starttime
            images = success + failure
            print "%d images in %ds (%.1fs/image), %d success, %d failure" % (images, delta, images/delta, success, failure) 
            print "******************************************************"
    if empty_run:
       break
    time.sleep(1)

