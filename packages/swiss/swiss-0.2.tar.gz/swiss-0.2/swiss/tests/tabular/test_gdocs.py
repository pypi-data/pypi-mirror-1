import swiss.tabular.gdocs as gdocs

# gdocs.Database

import gdata.spreadsheet.text_db

username = 'okfn.rufus.pollock'
password = 'penci12'

class TestGDocs:
    def test_1(self):
        client = gdata.spreadsheet.text_db.DatabaseClient(username=username,
                password=password)
        dbname = 'okfn-swiss-gdocs-testing'
        dbname = 'WDMMG Data Summary'
        dbs = client.GetDatabases(name=dbname)
        assert len(dbs) == 1, len(dbs)
        db = dbs[0]
        tab = db.GetTables(name='Sheet1')[0]
        rows = tab.GetRecords(15, 20)
        print len(rows)
        for row in rows:
            print row.content
        assert False

