'''TabularData from a Google Docs Spreadsheet.
'''

class GDocsReader():
    def __init__(self, filepath_or_fileobj=None, username=None, password=None):
        # do not pass filepath_or_fileobj down as it will be aurl or sheet name
        super(GDocsReader, self).__init__(None)
        self.source = filepath_or_fileobj
        self.username = username
        self.password = password
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        self.gd_client.email = username
        self.gd_client.password = password

    # is it possible to get it as csv
    def read(self, sheet_index=0):
        '''Load the specified google spreadsheet worksheet as a L{TabularData}
        object.

        @return L{TabularData} object.
        '''
        super(GDocsReader, self).read(None)
        self.gd_client.source = self.source
        self.gd_client.ProgrammaticLogin()
        feed = self.gd_client.GetSpreadsheetsFeed()
        assert len(feed) > 0, 'No spreadsheets found for: %s' % self.source
        wrksht_id = feed.entry[0].id.text.split('/')[-1]
        sheetfeed = self.gd_client.GetWorksheetsFeed(wrksht_id)
        sheet_id = sheetfeed.entry[sheet_index].id.text.split('/')[-1]
        cells_feed = self.gd_client.GetCellsFeed(wrksht_id, sheet_id)
        
        tdata = TabularData()
        # how do we get rows rather than just all the cells?
        for i, entry in enumerate(cells_feed.entry):
            tdata.data.append([entry.content.text])

