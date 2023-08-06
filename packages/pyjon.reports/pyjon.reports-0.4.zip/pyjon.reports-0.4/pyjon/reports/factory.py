import sys
import os
import tempfile
import shutil
from pyPdf import PdfFileWriter, PdfFileReader

from pyjon.reports import ReportTemplate
from genshi.template import TemplateLoader

import logging
logger = logging.getLogger()

class ReportFactory(object):
    def __init__(self, template_path=None, auto_reload=True):
        """
        Initializes the report factory.
        
        There is two way of using it :
        - Using create_tempfile to create temporary documents and writing
        manually in the temp files, calling check_last_tempfile afterwards and
        then calling render_document to write the final file
        - Using render_template to have the factory make the template render
        and feed it the correct arguments
        """
        self.tempfiles = list()
        self.documents = list()
        self.current_start_page = 0
        self.template_path = template_path or []
        self.templates_loader = None
        
        if template_path and not isinstance(template_path, list):
            self.template_path = [template_path]
            
        if self.template_path:
            self.templates_loader = TemplateLoader(self.template_path,
                                                   auto_reload=auto_reload)
        
    def create_tempfile(self):
        fname = self.__generate_tempfile()
        self.tempfiles.append(fname)
        return fname
    
    def check_last_tempfile(self):
        """
        This function checks the last tempfile and updates the start_page
        according to its page number
        """
        fileinst = open(self.tempfiles[-1], "rb")
        pdffile = PdfFileReader(fileinst)
        self.current_start_page += pdffile.numPages
        fileinst.close()
        
    def get_current_page_number(self):
        return self.current_start_page
    
    def __generate_tempfile(self):
        fd, fname = tempfile.mkstemp()
        os.close(fd)
        return fname
    
    def render_template(self,
                        template_string=None,
                        template_file=None,
                        **kwargs):
        if not template_string and template_file:
            if not self.templates_loader:
                template_file = open(template_file, 'r')
                template_string = template_file.read()
                template_file.close()
                template = ReportTemplate(template_string)
            else:
                template = self.templates_loader.load(template_file,
                                                      cls=ReportTemplate)
        elif template_string and not template_file:
            template = ReportTemplate(template_string,
                                      loader=self.templates_loader)
        else:
            raise ValueError("You should provide either a template string"
                            +" or a template file.")
        
        temp_filename = self.create_tempfile()
        template.render(temp_filename, **kwargs)
        self.check_last_tempfile()
        
    def render_document(self, out_filepath):
        """
        Joins all the page groups in the final pdf file
        """
        if len(self.tempfiles) > 1:
            self.join_documents(out_filepath)
        elif len(self.tempfiles) == 1:
            shutil.copy(self.tempfiles[0], out_filepath)
        else:
            raise ValueError('There was no file to render')
    
    def join_documents(self, out_filepath):
        output_pdf = PdfFileWriter()
        logger.debug("Created output pdf object")
        fileinsts = list()
        for filename in self.tempfiles:
            fileinst = open(filename, "rb")
            pdffile = PdfFileReader(fileinst)
            logger.debug("merging %s in output pdf" % filename)
            for pageNum in range(pdffile.numPages):
                page = pdffile.getPage(pageNum)
                output_pdf.addPage(page)
            fileinsts.append(fileinst)
            
        logger.debug("Writing output pdf to %s" % out_filepath)
        fileinst=open(out_filepath, "wb")
        output_pdf.write(fileinst)
        fileinst.close()
        for infileinst in fileinsts:
            infileinst.close()
    
    def cleanup(self):
        for filename in self.tempfiles:
            logger.debug("Removing temp file %s" % filename)
            os.remove(filename)
