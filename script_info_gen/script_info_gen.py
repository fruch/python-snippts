from Cheetah.Template import Template
import re
import os
#TODO: switch to MAKO

def readConfigFiles(settings_path):
    from configobj import ConfigObj
    
    input_files = []
    output_files = []
    
    config = ConfigObj(settings_path)
    
    #read  input filenames
    input_path = config['input_path']
    input_files = ["%s%s" % (input_path, x) for x in config['input_files']]

    #read output files and templates
    lines = config['output_files']
    for file in lines:
        output_files.append({"filename":config[file]['path_to_save'] + file,
                            "template":config[file]['template']
                            })
    return input_files, output_files
    
def parseIntoScriptList(input_files):
    script_list = []
    
    regexp_for_test = '/\*(?P<doc>.*?[^\*/])\*/.*?XSTATUS\s*(?P<func>.*?[^(])\(.*?SCRIPT_NAME\("(?P<name>.*?[^"])".*?return'

    for filename in input_files:
        lines = open(filename).read()
        print "processing ", filename
        regexp = re.compile(regexp_for_test, re.MULTILINE | re.DOTALL)
        res = regexp.finditer(lines)
        if res is not None:
            for match in res:
                script_list.append(
                        dict(name=str(match.group("name")),
                             subject=str(os.path.basename(filename)),
                             estimated=0,
                             func=str(match.group("func")),
                             doc=str(match.group("doc")))
                        )
    return script_list
                    

def useTemplates(script_list, output_files):
    for entry in output_files: 
        output = Template(entry["template"], searchList=[{'script_list' : script_list}])
        import pdb; pdb.set_trace()
        f = open(entry["filename"],"w+")
        f.write(str(output))
        f.close()

def usage():
    print '''
        script_info_gen [-s inifile]
        args:
            -s, --settings  inifile to load
            -h, --help      this help screen
    '''
    
def main():
    import getopt, sys

    settings_path = "settings.ini"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:", ["help", "settings="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
        
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--settings"):
            settings_path = a
        else:
            assert False, "unhandled option"

    input_files, output_files = readConfigFiles(settings_path)
    script_list = parseIntoScriptList(input_files)
    useTemplates(script_list, output_files)

if __name__ == "__main__":
    main()
