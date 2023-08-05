import pkg_resources
import sys
from optparse import OptionParser

group_name = 'lyricsearch.search'

        
def command():
    usage = "usage: %prog [options] title artist"
    parser = OptionParser(usage)
    parser.add_option('-p','--plugin', action="store", dest="plugin",help='Select a plugin to search')
    parser.add_option('-l','--list', action="store_true", dest="lista", help='List plugins available')
    (options, args) = parser.parse_args()
    if options.lista:
        print 'Plugins availables:'
        for ep in pkg_resources.iter_entry_points(group_name):
            print '--',ep.name
        sys.exit()    
    if len(args) != 2:
        parser.error('incorrect number of arguments')
    title = args[0]
    artist = args[1]
    if options.plugin:
        for ep in pkg_resources.iter_entry_points(group_name):
            if ep.name == options.plugin:
                plugin_class = ep.load()
                b = plugin_class()
                texto = b.find(title, artist)
                if texto:
                    print texto
                    sys.exit()
        print ''
    entry_points = []
    for ep in pkg_resources.iter_entry_points(group_name):
        entry_points.append(ep)
    for ep in entry_points:
        plugin_class = ep.load()
        print 'procurando com:',ep.name
        b = plugin_class()
        texto = b.find(title, artist)
        if texto:
            print texto
            break
        
if __name__ == '__main__':
    command()