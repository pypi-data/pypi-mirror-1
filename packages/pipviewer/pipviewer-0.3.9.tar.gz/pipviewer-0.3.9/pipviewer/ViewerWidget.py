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

import sys
import math
import pselfiles as PSF

from colorsys import hsv_to_rgb
from qt import *
from qtgl import *
from OpenGL.GL import *


#############################################################
#              G L O B A L   C O N S T A N T S
#############################################################

# OpenGL deepness (z)
FAR = 20.0
NEAR = -5.0

# Regions signals
NEW_REGION_SIG = PYSIGNAL("newRegion(str,int,int)")
NO_REGION_SIG = PYSIGNAL("noRegion()")
MAPPING_CHANGED_SIG = PYSIGNAL("mappingChanged()")

# Region types
SELECTION = 1
PROBE     = 2
BREAK     = 3
AUTOBREAK = 4
TRASH     = 5

# Region colors
COLORS = {SELECTION: (.0, .1, .9),
	  PROBE: (.1, .9, .0),
	  BREAK:  (.9, .0, .0),
	  TRASH:  (.5, .5, .5),}

	  
#############################################################
#              G L O B A L   F U C T I O N S
#############################################################
  
def axis_scale(range):
    """ Returns A [big, small] list of graduations and take the range 
    of the viewer window in parameter. Big is more spaced than small 
    and should receive a longer tick mark.
    """
    # TODO: those are not that good, must fix that
    if range < 20:
        return [10, 5]
    big = int(10**(math.floor(math.log(range/2)/math.log(10))))
    if range/big >= 10:
        big = big * 5
    elif range/big >= 5:
        big = big * 2
    
    return [big, big/5]

      
#############################################################
#                  M A I N   C L A S S
#############################################################

class ViewerWidget(QGLWidget):
    """ This class define a viewer window for visualising multiple 
    alignment and determine witch region are highly conserv and 
    witch are not. Regions on the aligment can be selected and set 
    as 'probe', 'break-point', or trash.
    """
    def __init__(self, parent=None, name=None):
        QGLWidget.__init__(self, parent, name)
        self.x = .0
        self.y = .0
        self.z = .0
        self.winSize = 0
        self.pos = 0
        self.selectStart = None
        self.selectStop = None
        
        # If set to True, the genes annotations are show.
        self.annotationsView = False
        
        
    def setWinSize(self, val):
        """ Mutator for setting the size of the viewer window. Take
        the value of the window size as parameter.
        """
        self.winSize = val
        self.update()


    def setPos(self, pos):
        """ Mutator for setting the position of the scroll bar
        on the viewer. Take the position of the scroll bar as 
        parameter.
        """
        self.pos = pos
        self.update()


    def setMapping(self, mapping):
        """ Mutator for setting the mapping containing the data view
        on th viewer. Take the hashMap containing the data as parameter.
        """
        self.refPosMap = {}
        self.mapping = mapping
        self.align = mapping[PSF.ALIGN]
        self.species = mapping[PSF.SPECIES]
        self.setViewAnnotationsState()
        
    
    def setViewAnnotationsState(self):
        """ Mutator that set the initial state of the genes annotations view 
        when the application is starting. If the annotations have been saved 
        in a .psel file, then they are automaticaly shown at startup.
        """
        if self.mapping[PSF.GENES_ANNOTATIONS]:
            self.annotationsView = True
        

    def setAnnotationsView(self, annotationsView):
        """ Mutator that set the view of the annotations on the viewer
        window.
        """
        self.annotationsView = annotationsView
        

    def mousePressEvent(self, event):
        """ Action performed when the user press the mouse button
        inside the viewer.
        """
        self.emit(NO_REGION_SIG, ())
        self.selectStop = None
        self.selectStart = self.toAlignPos(event.x())
        self.update()


    def mouseMoveEvent(self, event):
        """ Action performed when the user move the mouse inside the
        viewer.
        """
        if self.selectStart != None:
           self.selectStop = self.toAlignPos(min(event.x(), self.width()))
           self.update()
    
    
    def mouseReleaseEvent(self, event):
        """ Action performed when the user release the mouse button
        inside the viewer.
        """
        if self.selectStart != None and self.selectStop != None:
            self.show_region_align(self.selectStart, self.selectStop)
        else:
            self.select_highlight_region(event)
            self.update()
    
    
    def keyPressEvent(self, event):
        """ Action performed when the user press a certain key on the 
        keyboard.
        """
        if event.key() == event.Key_Escape:
            self.reset_region()
            event.accept()
        if event.key() in (event.Key_Backspace, event.Key_Delete): 
            self.clear_region()
            event.accept()
    
    
    def select_highlight_region(self, event):
        """ Select the possible highligh regions set on the viewer window. 
        The regions are selected when the user release the mouse button inside 
        any highlight regions.
        """
        event_x = self.toAlignPos(event.x())
        
        # Parse the highlighted region in the mapping
        for k, r_type in [(PSF.PROBES, PROBE),
                        (PSF.BREAKS, BREAK),
                        (PSF.TRASHS, TRASH)]:
            for i, reg in enumerate(self.mapping[k]):
                start, stop = reg
                if start <= event_x <= stop:
                    self.selectStart = start 
                    self.selectStop = stop
                    self.show_region_align(self.selectStart, self.selectStop)


    def getProbeSeq(self, x0, x1):
        """ Accessor that return the probe nucleotide sequence on the multiple 
        alignment. Take the the starting and ending position of the probe
        region as parameters.
        """
        return PSF.ref_genome_seq(self.mapping, x0, x1)


    def posToRefPos(self, pos):
        """ Return which nucleotide on the ref genome is mapped to pos
        on the multiple alignment """
        # FIXME: this function memorize for speedup but there is no cache
        # expiration
        val = self.refPosMap.get(pos, None)
        if not val:
            val = self.refPosMap[pos] = len(self.getProbeSeq(0, pos))
        return val
    
    
    def getSelection(self):
        """ Accessor that return the starting and ending positions
        of a selected region.
        """
        if self.selectStart != None and self.selectStop != None:
            x0 = min([self.selectStart, self.selectStop])
            x1 = max([self.selectStart, self.selectStop])
            return (x0, x1)


    # FIXME: those setRegionAsFOO() are quite similar and should be
    # merged
    def setRegionAsProbe(self):
        """ Mutator for setting the selected region as a 'Probe'. Annotations
        of the probes are saved to the mapping and the region on the viewer
        is define by a green clear rectangle. 
        """
        if self.getSelection():
            x0, x1 = self.getSelection()
            # clear Region to stop the texture being overdraw
            self.clear_region() 
            self.mapping[PSF.PROBES].append((x0, x1))
            self.mapping = PSF.next_probeName(self.mapping, x0, x1)
            self.mapping[PSF.PROBES].sort()
            self.emit(MAPPING_CHANGED_SIG, ())
            self.show_region_align(self.selectStart, self.selectStop)
            self.update()


    def setRegionAsBreakPoint(self):
        """ Mutator for setting the selected region as a 'Break-point'. 
        Annotations of the break-point are saved to the mapping and the region 
        on the viewer is define by a red clear rectangle.
        """
        if self.getSelection():
            x0, x1 = self.getSelection()
            # clear Region to stop the texture being overdraw
            self.clear_region() 
            self.mapping[PSF.BREAKS].append((x0, x1))
            self.emit(MAPPING_CHANGED_SIG, ()) 
            self.show_region_align(self.selectStart, self.selectStop)
            self.update()


    def setRegionAsTrash(self):
        """ Mutator for setting the selected region as 'Trash'. Annotations 
        of the trash are saved to the mapping and the region on the viewer 
        is define by a grey clear rectangle.
        """
        if self.getSelection():
            x0, x1 = self.getSelection()
            # clear Region to stop the texture being overdraw
            self.clear_region() 
            self.mapping[PSF.TRASHS].append((x0, x1))
            self.emit(MAPPING_CHANGED_SIG, ())
            self.show_region_align(self.selectStart, self.selectStop)
            self.update()


    def clear_region(self):
        """ Used to cleared a highlighted region when this region is selected 
        or when the selection window intersect the region.
        """
        if self.getSelection():
            x0, x1 = self.getSelection()
        
            def intersect(reg):
                return (x0 <= reg[0] <= x1) or (x0 <= reg[1] <= x1) \
                        or (reg[0] <= x0 <= reg[1]) or (reg[0] <= x1 <= reg[1])
        
            def not_intersect(reg):
                return not intersect(reg)
    
            for k in PSF.REGION_TYPES:
                self.mapping[k] = filter(not_intersect, self.mapping[k])
            
            # Keep the selection and show region aligned
            self.emit(NO_REGION_SIG, ())
            self.emit(MAPPING_CHANGED_SIG, ())    
            self.show_region_align(self.selectStart, self.selectStop)
            self.update()


    def reset_region(self):
        """ Used to reset the selection window at any moment.
        """
        self.selectStart = None
        self.selectStop = None
        self.emit(NO_REGION_SIG, ())
        self.update()


    def show_region_align(self, pos0, pos1):
        """ Show the local multiple alignment of a selected region. The 
        reference genomes is always the first on the alignment. Conserve 
        nucleotide are shown as dot ('.') on the other genomes.
        """
        beg = min([pos0, pos1])
        end = max([pos0, pos1])
        
        spec_width = max(map(len, self.species)) + 2
        ref = self.align[0][beg:end]

        def expand(str, spe):
            """ Internal function that return the list containing the 
            nucleotide of the multiple alignment and take the species
            name as parameter. 
            """
            if spe == self.species[0]:
                return str
            lst = []
            for r, c in zip(ref, str):
                if r == c and r != "-":
                    lst.append(".")
                else:
                    lst.append(c)
            return "".join(lst)

        lines = map(lambda seq, spe:("%-*s" % (spec_width, spe+":")) \
                + expand(seq[beg:end], spe), self.align, self.species)
        txt = "\n".join(lines)
        
        self.emit(NEW_REGION_SIG, (txt, beg, end))


    def draw_region_highlight(self, type, x0, x1):
        """ Draw the regions that have been set in the mapping on the viewer
        window. The possible region are 'Probes', 'Break-point' or 'Trash'.
        Take the region type, start position and end position as parameters.
        """
        # X value of the rectangle region
        beg = min([x0, x1])
        end = max([x0, x1])
        
        # Colors type
        r, g, b = COLORS[type]
        
        # Y value of the rectangle region
        lo = .07
        hi = .92
        if self.annotationsView == True:
            lo = .02
            hi = .6
        
        # Draw interior rectangle
        glColor4f(r, g, b, .2)
        glBegin(GL_QUADS)
        glVertex3f(beg, lo, -.2)
        glVertex3f(end, lo, -.2)
        glVertex3f(end, hi, -.2)
        glVertex3f(beg, hi, -.2)
        glEnd()

        # Draw contour rectangle
        glColor4f(r, g, b, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(beg, lo, -.25)
        glVertex3f(end, lo, -.25)
        glVertex3f(end, hi, -.25)
        glVertex3f(beg, hi, -.25)
        glColor4f(r/2, g/2, b/2, 1.0)
        glEnd()


    def draw_graduations(self, step, pad, labels):
        """ Draw the graduations with the label on the viewer window. Take
        the step (x value between eatch graduation), the pad (y value
        between the graduation and the viewer window) and the labels as
        parameters.  
        """
        # Define the labels
        start = self.pos - self.pos % step
        stop = stop = self.pos + self.winSize
        stop = stop - stop % step
        z = 3.0
        
        for i in range((stop - start)/step+1):
            n_pos = start + i*step
            x = self.posToGLView(n_pos)
            
            # Y value of the graduation
            grad_lo = pad
            grad_hi = 1.0-pad
            adjust = 1.0
            if self.annotationsView == True:
                grad_lo = .62-pad
                grad_hi = pad
                adjust = .6
            
            # Draw the graduation	
            glBegin(GL_LINES)
            glVertex3f(x, grad_lo, z)
            glVertex3f(x, grad_hi, z)
            glEnd()
            
            # Draw the labels
            if labels and x > .05:
                hi = adjust-pad*2
                x = self.posToGLView(n_pos+2)
                self.renderText(x, pad, z, str(n_pos))
                self.renderText(x, hi, z, str(self.posToRefPos(n_pos))) 


    def draw_annotations(self, alignAnnotations):
        """ Draw the genes annotations on the viewer window. Take 
        the list of the annotations on the multiple alignment as
        parameter.
        """
        # Define the strand type
        COMPLEMENT = '-'
        DIRECT = '+'
        
        for geneName, alignStart, alignStop, strandType in alignAnnotations:
            
            # X value for the annotations rectangle
            beg = self.posToGLView(alignStart)
            end = self.posToGLView(alignStop)
            
            # Define the color and Y value of the strand type
            if strandType == DIRECT:
                color = [17.0/255, 177.0/255, .0]
                hi = .80
                lo = .70
            else:
                color = [170.0/255, 0, 201.0/255]
                hi = .95
                lo = .85
            
            # Draw the interior rectangle
            glColor4f(*(color + [0.3]))
            glBegin(GL_QUADS)
            glVertex3f(beg, hi, .2)
            glVertex3f(beg, lo, .2)
            glVertex3f(end, lo, .2)
            glVertex3f(end, hi, .2)
            glEnd()
            
            # Draw the contour rectangle
            glColor4f(*(color + [1.0]))
            glBegin(GL_LINE_LOOP)
            glVertex3f(beg, lo, -.25)
            glVertex3f(end, lo, -.25)
            glVertex3f(end, hi, -.25)
            glVertex3f(beg, hi, -.25)
            glEnd()
            
            # Draw the genes names
            if self.winSize < self.width()*6:
                glColor4f(.0, .0, .0, 1.0)
                y = hi-.07
                x = beg + .005
                self.renderText(x, y, 1.0, geneName)
        
    
    def draw_axis(self):
        """ Draw the axis on the viewer window. The axis is composed of the
        big and small graduation and the labels.
        """
        # Define the X value of the axis
        stepBig, stepSmall = axis_scale(self.winSize)
        
        # Define the Y value of the axis
        padBig = .1
        padSmall = .2
        y_align = .1
        y_ref = .80
        if self.annotationsView == True:
            padBig = .03
            padSmall = .54
            y_align = .04
            y_ref = .54 
        
        # Draw the small graduation
        glColor4f(.0, .0, .0, .5)
        self.draw_graduations(stepSmall, padSmall, False)
        
        # Draw the big graduation
        glColor4f(.0, .0, .0, 1.0)
        self.draw_graduations(stepBig, padBig, True)
        
        # Draw the title of the axis
        glColor4f(.0, .0, .0, .6)
        self.renderText(.0, y_align, 3.0, "Align:")
        self.renderText(.0, y_ref, 3.0, "Ref:")
        
    
    def draw_conservation_curve(self, hi, mh, conservs):
        """ Draw the conservation curve on the viewer window. Take the 
        Y values of the upper conservation curve rectangle (hi), 
        of the lower conservation curve rectangle (mh) and the list of 
        conserved nucleotide as parameters.
        """
        if self.winSize < self.width()*6:
            glColor4f(0.0, 0.0, 0.0, 1.0)
            
            # Draw the conservation curve
            glBegin(GL_LINE_STRIP)
            for i in range(self.winSize):
                conserv = conservs[i]
                x = 1.0*i/self.winSize
                glVertex3f(x, mh+(hi-mh)*conserv, .0)
            glEnd()

    
    def draw_conservation_plots(self, hi, mh, ml, lo, conservs):
        """ Draw the conservation plots on the viewer window. Take the Y
        value of the upper and lower conservation curve rectangle (hi, mh), 
        of the upper and lower conservation plots rectangles (ml, lo) and
        the list of conserved nucleotide as parameters.
        """
        # Draw the black and white conservaition plots
        glBegin(GL_QUAD_STRIP)
        for i in range(self.winSize):
            conserv = conservs[i]
            r, g, b = hsv_to_rgb(conserv / 3, .85, .85)
            glColor4f(r, g, b, 1.0)
            x = 1.0*i/self.winSize
            glVertex3f(x, mh, .0)
            glVertex3f(x, ml, .0)
        glVertex3f(1.0, mh, .0)
        glVertex3f(1.0, ml, .0)
        glEnd()
        
        # Draw the colors conservation plots
        glBegin(GL_QUAD_STRIP)
        for i in range(self.winSize):
            conserv = conservs[i]
            glColor4f(.0, .0, .0, conserv)
            x = 1.0*i/self.winSize
            glVertex3f(x, ml, .0)
            glVertex3f(x, lo, .0)
        glVertex3f(1.0, ml, .0)
        glVertex3f(1.0, lo, .0)
        glEnd()
        
        # Draw the contour conservation plots rectangle
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        for y in [lo, ml, mh, hi]:
            glVertex3f(0.0, y, -.5)
            glVertex3f(1.0, y, -.5)
        glEnd()

    
    def draw_selection(self):
        """ Draw the selection window on the viewer window.
        """
        # Define the X value of the selection window
        if self.selectStart != None and self.selectStop != None:
            x0 = self.posToGLView(self.selectStart)
            x1 = self.posToGLView(self.selectStop)
            self.draw_region_highlight(SELECTION, x0, x1)
        
        # Define the Y value of the probe name label
        y0 = .93
        if self.annotationsView == True:
            y0 = .62
        
        # Draw the selection  
        for k, r_type in [(PSF.PROBES, PROBE),
                        (PSF.BREAKS, BREAK),
                        (PSF.TRASHS, TRASH)]:
            for i, reg in enumerate(self.mapping[k]):
                start, stop = reg
                x0 = self.posToGLView(start)
                x1 = self.posToGLView(stop)
                self.draw_region_highlight(r_type, x0, x1)
            
                # Draw the probes names
                if r_type == PROBE:
                    probeName = self.mapping[PSF.PROBES_IDS][(start, stop)]
                    self.renderText(x0, y0, .0, probeName)

    
    def paintGL(self):
        """ Draw the elements of the viewer window.
        """
        # Set the shade model depending of the window size
        if self.winSize > self.width()*6:
            glShadeModel(GL_FLAT)
        else:
            glShadeModel(GL_SMOOTH)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Define the list of conserved nucleotide on the alignment
        conservs = map(lambda i:PSF.conservation(self.mapping, self.pos+i),
                range(self.winSize))
        
        # Define the Y value of the conservations plots and curve
        hi = .76
        mh = .59
        ml = .42
        lo = .25
        
        # Draw the genes annotations
        if self.annotationsView == True:
            self.draw_annotations(self.mapping[PSF.GENES_ANNOTATIONS])
            hi = .5
            mh = .37
            ml = .25
            lo = .12
        
        # Draw the axis and the graduation
        self.draw_axis()
        
        # blank the axis just behind the convervation plots
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(.0, hi, .1)
        glVertex3f(.0, lo, .1)
        glVertex3f(1.0, lo, .1)
        glVertex3f(1.0, hi, .1)
        glEnd()

        # Draw the Conservation curve
        self.draw_conservation_curve(hi, mh, conservs)

        # Draw the Conservation plots
        self.draw_conservation_plots(hi, mh, ml, lo, conservs)
        
        # Draw the selection     
        self.draw_selection()
        

    def toGLView(self, x):
        """ Return the size of the viewer window to openGL values.
        """
        "map x in pixel in [0..1]"
        return 1.0*x/self.width()


    def toAlignPos(self, x):
        """ Return the size of the alignment window to openGL values.
        """
        "map x in pixel to [0..len(align[0])]"
        x = max(0, x)
        return self.pos + int(self.toGLView(x)*self.winSize)


    def posToGLView(self, pos):
        """ Return the position on the viewer window to openGL values.
        """
        "map pos in bp to [0..1]"
        #pos = min(pos, 0)
        return 1.0*(pos-self.pos)/self.winSize
    

    def rezoom(self):
        """ Used for setting the projection of the viewer window depending
        of the window size.
        """
        glViewport( 0, 0, self.width(), self.height() )
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho( .0, 1.0, .0, 1.0, NEAR, FAR)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef( self.x, self.y, self.z)
        self.update()


    def resizeGL(self, width, height):
        self.rezoom()


    def initializeGL(self):
        """ Set the openGL options parameters used in the viewer.
        """
        glShadeModel(GL_SMOOTH);
        glEnable(GL_CULL_FACE)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
    
        glEnable(GL_NORMALIZE)
