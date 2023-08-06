

class TableSorter(object):
    
    def __init__(self, id, data):
        self.id = id
        self.data = data

    def render(self):
        html = '<table id="'+self.id+'"><thead><tr>'
        for item in self.data[0]:
            html += '<th>'+str(item)+'</th>'
        html += '</tr></thead><tbody>'
        for row in self.data[1:]:
            html += '<tr>'
            for item in row:
                html += '<td>'+str(item)+'</td>'
            html += '</tr>'
        html += '</tbody></table>'
        html += '<script type="text/javascript">jq("#'+self.id+'").tablesorter();</script>'
        return html
