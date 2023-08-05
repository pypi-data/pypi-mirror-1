#!/usr/bin/python
#  Copyright (C) 2006-2007 Free Software Foundation

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


#############################################################
#            I M P O R T I N G   M O D U L E S
#############################################################

import os
import sys
import math
import tempfile
import utils

from qt import *
from utils import *

from shutil import rmtree
from ViewerGui import ViewerGui
from ViewerWidget import NEW_REGION_SIG, NO_REGION_SIG, MAPPING_CHANGED_SIG
from ScoreGui import ScoreGui
from SpeciesGenomesDialog import SpeciesGenomesDialog
from ProbesListDialog import SELECT_SIG, PROBE_START_POS, PROBE_STOP_POS, ProbesListDialog
from UserManuelGui import UserManuelGui
from pselfiles import load_mapping, save_mapping, FILE_FORMAT_EXT
import pselfiles as PSF
from pkg_resources import resource_filename
import pipviewer


#############################################################
#              G L O B A L   C O N S T A N T S
#############################################################

# the number of "pages" on the scrollbar resolution
PAGES = 200


#############################################################
#                  M A I N   C L A S S
#############################################################

class ViewerWin(ViewerGui):
    """ This class define a ViewerWin for visualise and setting differents
    parameters on a multiple alignment. These parameter includes the 
    setting of region type, the file manipulation, the views options and 
    the navigation inside the alignment.
    """
    def __init__(self,parent=None,name=None):
        ViewerGui.__init__(self,parent,name)
        self.connect(self.widthSpn, SIGNAL("valueChanged(int)"),
                    self.setWinSize)
        self.connect(self.scroll, SIGNAL("valueChanged(int)"),
                    self.viewer.setPos)
        self.connect(self.skipBtn, SIGNAL("clicked()"),
                    self.viewer.reset_region)
        self.connect(self.probeBtn, SIGNAL("clicked()"),
                    self.viewer.setRegionAsProbe)
        self.connect(self.breakPointBtn, SIGNAL("clicked()"),
                    self.viewer.setRegionAsBreakPoint)
        self.connect(self.trashBtn, SIGNAL("clicked()"),
                    self.viewer.setRegionAsTrash)
        self.connect(self.clearBtn, SIGNAL("clicked()"),
                    self.viewer.clear_region)
        self.connect(self.scoreBtn, SIGNAL("clicked()"),
                    self.check_score)
        self.connect(self.viewer, NEW_REGION_SIG, self.show_region)
        self.connect(self.viewer, NO_REGION_SIG, self.reset_region)
        self.connect(self.viewer, MAPPING_CHANGED_SIG, self.update_mapping_stats)
        self.connect(self.viewer, MAPPING_CHANGED_SIG, self.update_probes_list)

        self.regTypeBtnsOut = [self.scoreBtn, self.breakPointBtn,
        		self.probeBtn, self.trashBtn]	
        self.regTypeBtnsIn = [self.scoreBtn, self.breakPointBtn,
                        self.probeBtn, self.trashBtn, self.clearBtn]
        self.regTypeBtnsIntersect = [self.breakPointBtn, self.probeBtn, 
                        self.trashBtn]

        # Probes List Dialog
        self.probesList = ProbesListDialog()
        self.connect(self.probesList.lstViewProbesList, SELECT_SIG, self.select_probe)
 
        # User Manuel Dialog
        self.userManuel = UserManuelGui()        

        # If true, ask the user for saving change at closing
        self.dirty = False

        
    
    def setParam(self, mapping):
        """ Matator for setting the initial parameters when the application
        started. Take the hashMap containing the data of the alignment as
        parameter.
        """
        self.mapping = mapping
        self.viewer.update()
        self.viewer.setMapping(mapping)
        width = len(self.viewer.align[0])
        self.widthSpn.setMaxValue(width)
        self.widthSpn.setValue((width / PAGES) or width)
        self.numProbeLbl.setNum(len(mapping[PSF.PROBES]))
        self.setViewAnnotationsStatus()
        
    
    def setViewAnnotationsStatus(self):
        """ Mutator for setting the initial state of the 'View Genes
        Annotations' toggle menu item.
        """
        if self.mapping[PSF.GENES_ANNOTATIONS]:
            self.viewsShowGenesAnnotationsAction.setEnabled(True)
            self.viewsShowGenesAnnotationsAction.setOn(True)
            self.viewer.setAnnotationsView(True)
        else:
            self.viewsShowGenesAnnotationsAction.setOn(False)
            self.viewsShowGenesAnnotationsAction.setEnabled(False)
            self.viewer.setAnnotationsView(False)
    
    
    def setMapping(self, filename):
        """ Mutator for setting the mapping containing the data of the 
        multiple alignement. Take the filename as parameter.
        """
        self.file = filename
        mapping = load_mapping(filename)
        self.setParam(mapping)
        

    def setWinSize(self, val):
        """ Mutator for setting the size of the viewer window and
        scroll bar. Take the position of the scroll bar as parameter.
        """
        self.viewer.setWinSize(val)
        width = len(self.viewer.align[0])
        self.scroll.setMaxValue(width-val)
        self.scroll.setPageStep(val)
        
    
    def setButtonsState(self, beg, end):
        """ Mutator for setting the states of the different buttons present
        in the main window. The buttons are 'check score', 'skip', 'clear',
        'probe', 'break-point' and 'trash'. Take the begining and ending pos
        of the selection window as parameters.
        """
        # Untill proven guilty we are not in a hightlighted region
        for btn in self.regTypeBtnsOut:
            btn.setEnabled(True)
        
        # Parse the highlighted region in the mapping
        for k, typeBtn in [(PSF.PROBES, self.probeBtn), 
                        (PSF.BREAKS, self.breakPointBtn), 
                        (PSF.TRASHS, self.trashBtn)]:          
            for reg in self.mapping[k]:
                start, stop = reg
            
                # Button state when a hightlighted region is selected
                if beg == start and end == stop:
                    for btn in self.regTypeBtnsIn:
                        btn.setEnabled(True)
                    typeBtn.setEnabled(False)
            
                # Button state when the selection intersect with a hightlighted region
                if (beg < start <= end) or (beg <= stop < end) or (beg > start and end < stop):
                    for btn in self.regTypeBtnsIntersect:
                        btn.setEnabled(False)	
                    self.clearBtn.setEnabled(True)

        
    def closeEvent(self, event):
        """ Action performed when the user close the main application.
        """
        # Signal the user for saving modification before closing
        if self.dirty:
            msg = "The file %s has been modified.\n\nDo you want to save it?"\
                    %(repr(os.path.split(self.file)[1]))
            returnVal = QMessageBox.warning(self, "Close the program - pipviewer",
                        msg, QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
            if returnVal == QMessageBox.Yes:
                self.fileSave()
                event.accept()
            elif returnVal == QMessageBox.No:
                event.accept()
            elif returnVal == QMessageBox.Cancel:
                event.ignore()
        else:
            event.accept()


    def fileExit(self):
        self.close()


    def fileSave(self):
        """ Action performed when the user select the 'file-->save' 
        menu item.
        """
        save_mapping(self.mapping, open(self.file, "w"))
        self.dirty = False
        self.statusBar().message("File has been saved successfully");


    def fileOpen(self):
        """ Action performed when the user select the 'file-->open' 
        menu item.
        """
        returnVal = None
        
        # Signal the user for saving modification before opening a new file
        if self.dirty:
            msg = "The file %s has been modified.\n\nDo you want to save it before opening a new file?"\
                    %(repr(os.path.split(self.file)[1]))
            returnVal = QMessageBox.warning(self, "Open File - pipviewer", 
                        msg, QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
            if returnVal == QMessageBox.Yes:
                self.fileSave()
        
        # Open a file Dialog for opening file
        if returnVal != QMessageBox.Cancel: 
            fileName = QFileDialog.getOpenFileName(
                    os.path.split(self.file)[0],
                    "Probes (*.psel);; All(*.*)",
                    self,
                    "open file dialog",
                    "Choose a file to open" );
            
            # Open the file if it exist
            if fileName:
                try:
                    self.setMapping(unicode(fileName))
                    self.statusBar().message( "File has been opened successfully")
                except PSF.FileFormatError:
                    QMessageBox.warning(self, "Warning - pipviewer", 
                            "The file is not a valid pipviewer file.")
        
        
    def fileSaveAs(self):
        """ Action performed when the user select the 'file-->save as' 
        menu item.
        """
        # Open a file dialog for saving file
        fileName = QFileDialog.getSaveFileName(
                self.file,
                "Probes (*.psel)",
                self,
                "save file dialog;; All (*.*)",
                "Choose a filename to save under")
        
        # Signal the user if the file already exist
        if fileName:
            self.file = str(fileName.ascii())
            if os.path.isfile(unicode(fileName)):
                msg = "The file %s already exist. Do you want to overwrite it?"\
                        %(repr(os.path.split(self.file)[1]))
                returnVal = QMessageBox.warning(self, "Overwrite the file? - pipviewer", 
                            msg, QMessageBox.Yes, QMessageBox.No)
            
                # Save the file to local disk
                if returnVal == QMessageBox.Yes:
                    save_mapping(self.mapping, open(unicode(fileName), "w"))
            else:
                save_mapping(self.mapping, open(unicode(fileName), "w"))
            
            self.dirty = False
            self.statusBar().message( "File has been saved successfully")
        

    def fileMerge(self):
        """ Action performed when the user select the 'file-->merge' 
        menu item.
        """
        # FIXME: this should go in pselfiles.py
        # Open a file dialog for opening file
        fileName = QFileDialog.getOpenFileName(
                "",
                "Probes (*.psel);; All(*.*)",
                self,
                "open file dialog",
                "Choose a file to open" );
        
        # Open the file if it exist
        if fileName:
            newMap = load_mapping(open(unicode(fileName)))
            
            # Merge the new file with the one in use
            if newMap[PSF.ALIGN] == self.mapping[PSF.ALIGN]:
                oldMap = self.mapping
                for k in PSF.REGION_TYPES:
                    oldMap[k] = remove_dups(oldMap[k]+newMap[k])
                self.update_mapping_stats()
            else:
                msg = "Can't merge probes from different alignments"
                QMessageBox.critical(self, "Bad Align", msg, True)

    
    def fileExportProbes(self):
        """ Action performed when the user select the 'file-->export probes' 
        menu item.
        """
        #Open a file dialog for chosing directory
        dir = QFileDialog.getExistingDirectory("")
        
        # Chose a suffix if dir exist
        if dir:
            suffix, ok = QInputDialog.getText("Probe Set Suffix", "Enter a suffix (optional):")
            suffix = ok and str(suffix) or ""
            probes = self.mapping[PSF.PROBES]
            probes.sort()

            label_width = int(math.floor(math.log10(len(probes)))+1)
            ref = self.getProbeSeq(0, len(self.mapping[PSF.ALIGN][0]))
            
            # Export the probe to file in the selected directory
            for i, probe in enumerate(probes):
                data = self.getProbeSeq(*probe)
                pos = ref.find(data)
                name = self.mapping[PSF.PROBES_IDS][probe]
                filename = os.path.join(str(dir), name + ".fas")
                annot = name+" "+self.mapping[PSF.SPECIES][0]+" " + \
                        str(pos+1)+":"+str(pos+len(data))
                print filename
                body = "\n".join(slice_fas(data))
                open(filename, "w").write(">%s\n%s\n" % (annot, body))

    
    def import_file(self, mapping, fileName):
        """ Import different multiple alignement file and save their
        content to the mapping. File can be ClustalW or PipMaker. Take
        the filename and the hashMap containing the data of the
        alignment as parameters.
        """
        self.setParam(mapping)
        # FIXME: we should be able to use unicode here
        base = os.path.splitext(str(fileName.ascii()))
        self.file = base[0] + PSF.FILE_FORMAT_EXT
        self.dirty = True
    
    
    def fileImportPipmaker(self):
        """ Action performed when the user select the 'file -> Import
        -> Pipmaker Multiple Alignement' menu item.
        """
        returnVal = None
        
        # Signal the user for saving modification before importing
        if self.dirty:
            msg = ("The file %s has been modified.\n\n"
                   "Do you want to save it before importing a new file?")
            msq = msg % (repr(os.path.split(self.file)[1]))
            returnVal = QMessageBox.warning(self, "Import File - pipviewer", 
                                            msg,
                                            QMessageBox.Yes,
                                            QMessageBox.No,
                                            QMessageBox.Cancel)
            if returnVal == QMessageBox.Yes:
                self.fileSave()
        
        # Open a file dialog for opening file
        if returnVal != QMessageBox.Cancel: 
            fileName = QFileDialog.getOpenFileName(
                "",
                "PipMaker Alignment File (*.txt);; All(*.*)",
                self,
                "open file dialog",
                "Choose a file to import");
            
            # Import the Pipmaker file if it exist
            if fileName:
                try:
                    mapping = PSF.import_multipipmaker_file(unicode(fileName))
                    self.import_file(mapping, fileName)
                    self.statusBar().message( "File has been imported successfully")
                except:
                    QMessageBox.warning(self, "Warning - pipviewer", 
                        "The file is not a valid Multipipmaker multiple alignment.")
    
    
    def fileImportClustal(self):
        """ Action performed when the user select the 'file-->Import-->ClustalW 
        Multiple Alignement' menu item.
        """
        returnVal = None
        
        # Signal the user for saving modification before importing
        if self.dirty:
            msg = "The file %s has been modified.\n\nDo you want to save it before importing a new file?"\
                    %(repr(os.path.split(self.file)[1]))
            returnVal = QMessageBox.warning(self, "Import File - pipviewer", 
                        msg, QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
            if returnVal == QMessageBox.Yes:
                self.fileSave()
        
        # Open a file dialog for opening file
        if returnVal != QMessageBox.Cancel: 
            fileName = QFileDialog.getOpenFileName(
                "",
                "ClustalW Alignment File (*.aln);; All(*.*)",
                self,
                "open file dialog",
                "Choose a file to import");
            
            # Import the ClustalW file if it exist
            if fileName:
                try:
                    mapping = PSF.import_clustalw_file(unicode(fileName))
                    self.import_file(mapping, fileName)
                    self.statusBar().message( "File has been imported successfully")
                except:
                    QMessageBox.warning(self, "Warning - pipviewer", 
                        "The file is not a valid ClustalW multiple alignment.")
     
    
    def viewShowAnnotations(self):
        """ Action performed when the user select the toggle menu item 
        'Views-->View Genes Annotations'. This item is only active if the 
        genes annotations have been compute or saved in the .psel file
        """
        if self.viewsShowGenesAnnotationsAction.isOn():
            self.viewer.setAnnotationsView(True)
            self.viewer.update()
        else:
            self.viewer.setAnnotationsView(False)
            self.viewer.update()

    
    def viewProbesList(self):
        """ Action performed when the user select the menu item 'Views-->
        Probes List'.
        """
        self.probesList.show()
        self.probesList.raiseW()
        self.probesList.setActiveWindow()
        

    def toolAssociateGenome(self):
        """ Action performed when the user select the menu item 'Tools-->
        Associate Genomes'.
        """
        dia = SpeciesGenomesDialog(self)
        speciesNumber = 0
        
        # Fill the genomes listView with the acession number in the mapping
        for i, species in enumerate(self.mapping[PSF.SPECIES]):
            speciesNumber = speciesNumber + 1
            if i == 0:
                QListViewItem(dia.genomesLst, str(speciesNumber), species+"(ref)",
                            self.mapping[PSF.REFSEQ_IDS].get(i, ""))
            else:
                QListViewItem(dia.genomesLst, str(speciesNumber), species, 
                            self.mapping[PSF.REFSEQ_IDS].get(i, ""))
        
        okVal = dia.exec_loop()
        
        # Add the accession number from the listView to the mapping
        if dia.Accepted == okVal: 
            item = dia.genomesLst.firstChild()
            while item:
                noSpecies = int(str(item.text(0)))-1
                self.mapping[PSF.REFSEQ_IDS][noSpecies] = unicode(item.text(2))
                item = item.nextSibling()
            self.dirty = True
    
     
    def toolComputeAnnotations(self):
        """ Action performed when the user select the menu item 'Tools-->
        Compute Genes Annotations'.
        """
        alignRefGenome = self.mapping[PSF.ALIGN][0]
        genomeLengthWithoutIR = self.viewer.posToRefPos(len(alignRefGenome))
        oldCursor = QCursor(self.cursor())
        waitCursor = QCursor(Qt.WaitCursor)
        
        # Compute the genes annotations from a genbank file if not present in
        # the mapping
        if not self.mapping[PSF.GENES_ANNOTATIONS]:
            self.setCursor(waitCursor)
            self.alignTxt.setCursor(waitCursor)
            try: 
                refGenomeFile = utils.genome_file(self.mapping, 0, "gb", True)
                annotations = utils.ref_genome_annotations(refGenomeFile, genomeLengthWithoutIR)
                alignAnnotations = utils.adjust_annotations_on_align(annotations, alignRefGenome)
                self.mapping[PSF.GENES_ANNOTATIONS] = alignAnnotations
                self.viewer.update()
                self.statusBar().message("Computation terminated.")
                self.setCursor(oldCursor)
                self.alignTxt.setCursor(oldCursor)
                self.dirty = True
                self.setViewAnnotationsStatus()
            except Exception:
                self.setCursor(oldCursor)
                self.alignTxt.setCursor(oldCursor)
                msg = "Cannot compute the ref. genome without his accession number.\
                        \n\nUse the 'Associate Genomes..' function to chose the accession number of the ref. genome."
                QMessageBox.warning(self, "Warning - Pipviewer", msg)
        else:
            msg = "Compute of genes annotation has already been performed or saved."
            QMessageBox.information(self, "Information - Pipviewer", msg)
    
    
    def helpUserManuel(self):
        """ Action performed when the user select the menu item 'help-->
        User Manuel'.
        """
        self.userManuel.txtBrwUserMan.setTextFormat(Qt.RichText)
        path = resource_filename(pipviewer.__name__, "guide.html")
        txt = unicode(open(path).read(), "utf-8")
        self.userManuel.txtBrwUserMan.setText(txt)
        self.userManuel.show()
        self.userManuel.raiseW()
        self.userManuel.setActiveWindow()

     
    def helpAbout(self):
        """ Action performed when the user select the menu item 'Help->about'.
        """
        msg = ("pipviewer %s \n"
               "Visualize multiple alignments and annotate regions.\n"
               ) % pipviewer.__version__
        QMessageBox.information(self, "About pipviewer", msg, True)


    def update_mapping_stats(self):
        """ Update the mapping data each time the user set a new probe.
        """
        self.numProbeLbl.setNum(len(self.mapping[PSF.PROBES]))
        self.dirty = True

    
    def update_probes_list(self):
        """ Update the probes list view each time the user set a new probe.
        """
        self.probesList.lstViewProbesList.clear()
        for i, probes in enumerate(self.mapping[PSF.PROBES]):
            probeName = self.mapping[PSF.PROBES_IDS][probes]
            start = probes[0]
            stop = probes[1]
            length = stop-start
            QListViewItem(self.probesList.lstViewProbesList, str(i+1), probeName, 
                        str(start+1), str(stop), str(length))

    
    def select_probe(self, item):
        """ Loacate and select the probe selected in the probes list. 
        Take the item selected from the probes list as parameter.
        """
        probeLocation = ()
        
        if item:
            start = int(str(item.text(PROBE_START_POS)))
            stop = int(str(item.text(PROBE_STOP_POS)))
            probeLocation = (start-1, stop)
            
            # Locate the probe in the conservation viewer
            adjustPos = (self.widthSpn.value()/2)-((stop-start)/2)
            self.scroll.setValue(start-adjustPos)
            
            # Select the probe
            self.viewer.selectStart = start-1
            self.viewer.selectStop = stop
            self.viewer.update()
            
            # Set the button state
            self.setButtonsState(start-1, stop)
        
        
    def getProbeSeq(self, x0, x1):
        """ Accessor that return a probe's nucleotide sequence. Take the starting
        and ending position as parameters.
        """
        return self.viewer.getProbeSeq(x0, x1)


    def check_score(self):
        """ Action performed when the user press the button 'Check Score'. This
        button is only active when their is a selected region in the viewer.
        """
        #TODO : Implement a dynamique global alignment algorithm
        oldCursor = QCursor(self.cursor())
        waitCursor = QCursor(Qt.WaitCursor)
        
        # Check the score of a selected region by using Blast2seq
        if self.viewer.getSelection():
            self.setCursor(waitCursor)
            self.alignTxt.setCursor(waitCursor)
            x0, x1 = self.viewer.getSelection()
            region = self.getProbeSeq(x0, x1)
            m_dir = tempfile.mkdtemp()
            res_dir = tempfile.mkdtemp()

            open(os.path.join(m_dir, "probe"), "w").write(
            ">probe\n%s\n" % region)
            
            cmd = "vhybridize -l 0 -i 0 -p %s -o %s " % (m_dir, res_dir)
            # FIXME: auto d/l should be configurable
            genomes = []
            try:
                # Download the species genomes
                genomes = filter(lambda s:s,
                        [genome_file(self.mapping, i, "fasta", True)
                        for i in range(len(self.mapping[PSF.SPECIES]))])
                if not genomes:
                    raise EOFError("Warning! No Acession Number")
                
                revMap = {}
                genomes = []
                for i, species in enumerate(self.mapping[PSF.SPECIES]):
                    genome = genome_file(self.mapping, i, "fasta", True)
                    if genome:
                        genomes.append(genome)
                        revMap[os.path.splitext(os.path.basename(genome))[0]] = species
                
                full_cmd = cmd + " ".join(genomes)
                print "full_cmd:", full_cmd
            
                # call vHybridize.py
                if os.system(full_cmd):
                    raise OSError("problems with vhybridize.py")

                dia = ScoreGui(self)

                # parse vhybridize output
                for f in filter(lambda f:os.path.splitext(f)[1] == ".vhy",
                                os.listdir(res_dir)):
                    #(start, stop, marker, %length, %identity)
                    lines = filter(lambda l:l and l[0] == "(",
                    open(os.path.join(res_dir, f)).readlines())

                    # FIXME: eval is not safe, we need proper parsing
                    lines = map(eval, lines)
                    lines = [(line[3], line[4], line) for line in lines]
                    lines.sort()
                    line = lines[-1][-1]
                    start, stop, name, length, identity = line[:5]

                    # FIXME: use the species name, not the filename
                    item = QListViewItem(dia.hitsLst,
                            revMap[os.path.splitext(f)[0]],
                            str(length),
                            str(identity))

                # cleanup
                rmtree(m_dir)
                rmtree(res_dir)
                self.setCursor(oldCursor)
                self.alignTxt.setCursor(oldCursor)

                dia.show()
                #print "region:", region
            
            except URLError:
                self.setCursor(oldCursor)
                self.alignTxt.setCursor(oldCursor)
                QMessageBox.warning(self, "Warning - pipviewer", 
                    "One or many accession number are invalid.")
            except EOFError:
                self.setCursor(oldCursor)
                self.alignTxt.setCursor(oldCursor)
                msg = ("There is no accession number associated with the"
                       " species genomes. \n"
                       "Use the 'tools -> associate genomes' option to"
                       " specify the accession numbers.")
                QMessageBox.warning(self, "Warning - pipviewer", msg)
            except OSError:
                self.setCursor(oldCursor)
                self.alignTxt.setCursor(oldCursor)
                msg = ("Problems with 'vhybidize'. \n"
                       "Is it installed properly?")
                QMessageBox.warning(self, "Warning - pipviewer", msg)

    
    def reset_region(self):
        """ Reset the informations showing when no region is selected in the
        viewer.
        """
        for btn in self.regTypeBtnsIn:
            btn.setEnabled(False)
        
        # Reset the text field that show the selected region
        self.alignTxt.clear()
        
        # Reset the reference sequence information
        self.startLbl.setText("-")
        self.stopLbl.setText("-")
        self.lengthLbl.setText("-")
        
        # Reset the alignment sequence information
        self.probeStartLbl.setText("-")
        self.probeStopLbl.setText("-")
        self.probeLengthLbl.setText("-")

    
    def show_region(self, txt, beg, end):
        """ Show the various informations when a region is selected in the
        viewer. Take the aligned sequences text and the begining and ending
        position of the selected region in the viewer as parameters.
        """
        # Set the aligned nucleotide sequences in the text field window
        self.alignTxt.clear()
        self.alignTxt.setText(txt)
        
        # Set the starting and ending position of the selection
        self.startLbl.setNum(beg+1)
        self.stopLbl.setNum(end)
        m_start = self.viewer.posToRefPos(beg)
        m_len = len(self.getProbeSeq(beg, end))
        self.probeStartLbl.setNum(m_start+1)
        self.probeStopLbl.setNum(m_start + m_len)
        
        # Set the selected region length
        self.lengthLbl.setNum(end-beg)
        self.probeLengthLbl.setNum(m_len)
        
        # Set the button states
        self.setButtonsState(beg, end)
        
        
def qt_run(filename):
    """ Set the application parameters and show the main window at startup.
    Take the filename as parameter.
    """
    app = QApplication(sys.argv)
    win = ViewerWin()
    win.setMapping(filename)
    app.setMainWidget(win)
    win.show()
    app.exec_loop()


def main():
    if len(sys.argv) != 2:
        print "USAGE: %s FILE" % sys.argv[0]
        print "  where FILE is a .psel file",
        sys.exit(1)
    else:
        qt_run(sys.argv[1])
    
if __name__ == "__main__":
    main()
