"""
Created on Apr 2021

@author: Gonzalo Valdés
mail:gonzalovaldescernuda@gmail.com

Script to generate the pdf report based on the FPDF package. Further documentation
can be found in the package's website
If charts generated are modified this script needs to be also modified.
Need to input figure size of the charts, number of columns and the titles to be 
shown in the pdf.
"""

from fpdf import FPDF
import os

# pdf=PDF(format='A3') #page format. A4 is the default value of the format, you don't have to specify it.
# PDF(orientation={'P'(def.) or 'L'}, measure{'mm'(def.),'cm','pt','in'}, format{'A4'(def.),'A3','A5','Letter','Legal')
# #default
# pdf = PDF(orientation='P', unit='mm', format='A4')  

figure_size = [9,4.8]
aspect_ratio = figure_size[1]/figure_size[0]
# n_rows = [3,3,3,3]
n_columns = 4
titles = ['Rev/Income/CF','Financing','Valuation 1','Valuation 2']


frame_dist = 12
inbet_dist = 5
width = (420 - frame_dist*2 - 4*inbet_dist)/n_columns

n_columns_tech = 3
width_tech = (420 - frame_dist*2 - 4*inbet_dist)/n_columns_tech
    
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

    def charts_fund(self,aspect_ratio):
        #Generate the charts for the fundamental analysis pdf
        # fpdf.image(name, x = None, y = None, w = 0, h = 0, type = '', link = '')
        
        height = width*aspect_ratio
        png_files = os.listdir(os.getcwd())
        
        #Go through all the png files in the folder
        for x in png_files:
            try:
                aux = x.replace('.','_').split('_')
                #Condition to define that it is an image used for fundamental analysis
                if aux[0]=='set2':
                    if (aux[1]=='1') & (aux[2]=='4'):
                        n_w = 300
                        self.image(str(os.getcwd())+ '\\' + x, 
                                   x = 1+frame_dist + (width+inbet_dist)*(float(aux[1])-1),
                                   y = frame_dist + 8 + (height)*(float(aux[2])-1)-30, w = n_w, h = n_w*aspect_ratio)
                    else:  
                        self.image(str(os.getcwd())+ '\\' + x, 
                                   x = 1+frame_dist + (width+inbet_dist)*(float(aux[1])-1),
                                   y = frame_dist + 8 + (height)*(float(aux[2])-1), w = width-2, h =height)
                else:
                    continue
            except:
                continue
        self.image(str(os.getcwd())+ '\\' + 'set2_1_3.png', 
                    x = 1+frame_dist + (width+inbet_dist)*(float(1)-1),
                    y = frame_dist + 8 + (height)*(float(3)-1), w = width-2, h =height)
        
    def charts_tech(self,aspect_ratio):
         #Generate the charts for the technical analysis pdf
        # fpdf.image(name, x = None, y = None, w = 0, h = 0, type = '', link = '')
        height = width_tech*aspect_ratio
        png_files = os.listdir(os.getcwd())
        
        #Go through all the png files in the folder
        for x in png_files:
            try:
                aux = x.replace('.','_').split('_')
                #Condition to define that it is an image used for technical analysis
                if aux[0]=='set3':
                    self.image(str(os.getcwd())+ '\\' + x, 
                                   x = 1+frame_dist + (width_tech+inbet_dist)*(float(aux[1])-1),
                                   y = frame_dist + 8 + (height)*(float(aux[2])-1), w = width_tech -2, h =height)
                else:
                    continue
            except:
                continue


                     
def run_pdf_fund(ticker):
    #Generate the pdf
    pdf = PDF(orientation='L', unit='mm', format='A3')
    pdf.add_page()
    # pdf.frames(aspect_ratio,n_columns,n_rows)
    pdf.titles(n_columns,titles)
    pdf.charts_fund(aspect_ratio)
    pdf.output('{0}fund_report.pdf'.format(ticker),'F')

def run_pdf_tech(ticker):
    #Generate the pdf
    pdf = PDF(orientation='L', unit='mm', format='A3')
    pdf.add_page()
    # pdf.frames(aspect_ratio,n_columns,n_rows)
    # pdf.titles(n_columns,titles)
    pdf.charts_tech(aspect_ratio)
    pdf.output('{0}tech_report.pdf'.format(ticker),'F')
