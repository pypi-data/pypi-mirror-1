# very dirty bach OCR transfer to DoDoStorage

import os, re, time, shutil, sys
import pySoftM.mpl
import dodostorage.client

docstore = dodostorage.client.StorageEngine('http://storage.local.hudora.biz:8000/')

def handle_file(inputpath):
    filename = os.path.basename(inputpath)
    if len(filename.split('-')) == 4:
        foo, auftragsnummer, vorgangsnummer, foo = filename.split('-')    
    else:
        auftragsnummer, vorgangsnummer, foo = filename.split('-')
    rows = pySoftM.mpl.get_mplvorgang(vorgangsnummer)
    if rows:
        print auftragsnummer, vorgangsnummer, rows[0]
        # {'komissionierbeleg_date': datetime.date(2007, 5, 15),
        #  'kundennummer': u'12610', 'vorgangsnummer': 40123424, 
        #  'rechnungsempfaenger': u'22838',
        #  'lieferschein': datetime.datetime(2007, 5, 15, 13, 35, 30),
        # 'kundennumer': u'22838', 'lieferschein_date': datetime.date(2007, 5, 15),
        # 'sachbearbeiter_bearbeitung': 29,
        #  'lieferscheinnr': 409603, 'auftragsnr': 182704,
        # 'komissionierbeleg_time': 131914, 'bestellnr': 0,
        # 'lieferschein_time': 133530, 'sachbearbeiter_rueckmeldung': 77,
        # 'auftragsnummer': 155195,
        #  'komissionierbeleg': datetime.datetime(2007, 5, 15, 13, 19, 14),
        # 'erfassungs_date': datetime.date(2007, 5, 14), 'auftragsart': u'ME'}
        if int(auftragsnummer) != int(rows[0]['auftragsnummer']):
            print "XXXXXXXX inconsistent", repr((auftragsnummer,rows[0]['auftragsnummer']))
        else:
            row = rows[0]
            start = time.time()
            print "Saving"
            docstore.add(open(inputpath).read(), category='Komissionierbeleg',
                         document_timestamp=row['letzter_kommissionierbeleg_date'],
                         contenttype='image/png',
                         attributes=dict(mpl_vorgang=row['vorgangsnummer'],
                         lieferscheinnummer=row['lieferscheinnr'],
                         auftragsnummer=row['auftragsnummer'],
                         kundennummer=row['kundennummer'],
                         rueckmeldung_durch=row['sachbearbeiter_rueckmeldung']))
            # os.unlink(inputpath)
            # shutil.move(inputpath, os.path.join('/home/md/batchscan/files/trash', filename))
            print "%.3fs" % (time.time() - start)
    else:
        print "nichts gefunden fuer", auftragsnummer, vorgangsnummer
    
for root, dirs, files in os.walk('/usr/home/md/tauzerodata/files/'):
    print root
    for filepath in [os.path.join(root, name) for name in files]:
        if os.path.exists(filepath) and filepath.endswith('.png'):
            print "found", filepath
            handle_file(filepath)

