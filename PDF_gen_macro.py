# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 17:43:11 2021

@author: gonza
"""

from fpdf import FPDF
import os

# pdf=PDF(format='A3') #page format. A4 is the default value of the format, you don't have to specify it.
# PDF(orientation={'P'(def.) or 'L'}, measure{'mm'(def.),'cm','pt','in'}, format{'A4'(def.),'A3','A5','Letter','Legal')
# #default
# pdf = PDF(orientation='P', unit='mm', format='A4')  

figure_size = [9,4.8]
aspect_ratio = figure_size[1]/figure_size[0]
n_rows = [3,3,2,2,3]
n_columns = 5
titles = ['GDP-Debt','Inflation','Yield','FED Balance','Volatility']
frame_dist = 12
inbet_dist = 5
width = (420 - frame_dist*2 - 4*inbet_dist)/n_columns
    
class PDF(FPDF):
    # def frames(self, aspect_ratio, n_columns, n_rows):
        
        # for x in range(n_columns):
        #     self.rect(frame_dist + (width+inbet_dist)*x, frame_dist,
        #               width,width*aspect_ratio*n_rows[x]+ 15)
        
    def titles(self,n_columns,titles):
        self.set_font('Arial', 'B', 12)
        self.set_y(frame_dist+4)
        # self.cell(ln=0, 15, ln=2, frame_dist+2,txt = titles[0])
        for x in range(n_columns):
            self.set_x(frame_dist + (width+inbet_dist)*x + width/2)
            self.cell(1,txt = titles[x],align = 'C')

    def charts(self,n_columns,aspect_ratio):
        # fpdf.image(name, x = None, y = None, w = 0, h = 0, type = '', link = '')
        
        height = width*aspect_ratio
        png_files = os.listdir(os.getcwd())
        for x in png_files:
            try:
                aux = x.replace('.','_').split('_')
                self.image(str(os.getcwd())+ '\\' + x, 
                           x = 1+frame_dist + (width+inbet_dist)*(float(aux[1])-1),
                           y = frame_dist + 8 + (height)*(float(aux[2])-1), w = width-2, h =height)
            except:
                continue
            
def run_pdf():
    pdf = PDF(orientation='L', unit='mm', format='A3')
    pdf.add_page()
    # pdf.frames(aspect_ratio,n_columns,n_rows)
    pdf.titles(n_columns,titles)
    pdf.charts(n_columns,aspect_ratio)
    pdf.output('macro_report.pdf','F')

