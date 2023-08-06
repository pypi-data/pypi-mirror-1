
class FlotGraph(object):
    """ FlotGraph """

    def __init__(self, type, id, width, height, data, options, extra):
        self.type = type
        self.id = id
        self.width = width
        self.height = height
        self.data = data
        self.options = options
        self.extra = extra

    def render(self):
        html = '<div id="'+self.id+'" style="'
        html += 'width:'+str(self.width)+'px;'
        html += 'height:'+str(self.height)+'px"></div>'
        html += '<script type="text/javascript">jq.plot(jq("#'+self.id+'"), ['
        delimiter = ''
        for item in self.data:
            html += delimiter+'{label:"'+item['label']+'", data:'+str(item['data'])+'}'
            delimiter = ', '
        
        html += '], {'+self.type+': {'
        delimiter = ''
        for name, value in self.options.iteritems():
            html += delimiter+name+': '+str(value)
            delimiter = ', '
        
        html += '}'

        for name, options in self.extra.iteritems():
            html += ', '+name+': {'
            delimiter = ''
            for option, value in options.iteritems():
                html += delimiter+option+': '+str(value)
                delimiter = ', '
            html += '}'
        return html + '});</script>'

        
