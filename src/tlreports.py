import tlproject
from tllogger import logger

import subprocess
from os import listdir
import numpy as np

class Reports:
    pdf_processes = list()
    def __init__(self, infos):
        self.infos = infos

    def show_pdfs(self, borehole_id):
        try:
            report_references = tuple(map(str, np.unique(self.infos[(self.infos['borehole_id'] == borehole_id)]['report_reference'].values))) #  iloc#[0]
            logger.debug('Open reports: ' + str(report_references))

            all_files = set(listdir(tlproject.path_pdfs))
            #files = tuple(f"{name}.pdf" for name in report_references if f"{name}.pdf" in all_files)
            files = tuple(
                f for f in all_files
                if any(f.startswith(name) and f.endswith(".pdf") for name in report_references)
            )

            #files = [f for f in listdir(tlproject.path_pdfs) if f.startswith(report_references)]

            for file in files:
                self.pdf_processes.append(subprocess.Popen(['evince', tlproject.path_pdfs + '/' + file],
                                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        except FileNotFoundError as e:
            logger.error(f"{e}")
        except Exception as e:
            logger.error(f"{e}")