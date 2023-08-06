import sys, os
sys.path.append('..')

from spats import SimplePageTemplateServer

root = os.path.abspath(os.path.dirname(__file__))

config = {
    "html_dir":[ 
        os.path.abspath("%s/html" % root),
        ],
    "scripts_dir":[ 
        os.path.abspath("%s/scripts" % root),
        ],
    "macros_templates": [ 
        os.path.abspath("%s/../templates/registry.pt" % root),
        os.path.abspath("%s/../templates/text.pt" % root),
        os.path.abspath("%s/../templates/text_lines.pt" % root),
        os.path.abspath("%s/../templates/boolean.pt" % root),

    ],
    "extra_context":None,
    "debug_mode":True
}

print config

def main():
    SimplePageTemplateServer.start(config=config)

if __name__=='__main__':
    main()
