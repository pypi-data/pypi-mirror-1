import os

from distutils.cmd import Command
from distutils import log
from docutils.core import publish_file

class build_docs(Command):
    description = "build documentation"
    user_options = [
        # ('optname=', None, ""),
    ]
    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass
        
    def run(self):
        """build end-user documentation."""
        readmeDir = "./blogmaker/blog/media/release/"
        if not os.path.isdir(readmeDir):
            os.makedirs(readmeDir)
        body = publish_file(open("./README.txt", 'r'),
                    destination=open(os.path.join(readmeDir, "README.html"), 'w'),
                    writer_name='html',
                    settings_overrides=dict(stylesheet_path='./setup/blogmaker.css',
                        strip_comments=True),
                    )
        log.info("published docs to: ./blogmaker/blog/media/release/README.html")
        