import pandas as pd
import numpy as np
import re
import requests
import sqlite3
from bokeh.plotting import figure, show
from bokeh.models import Span, ColumnDataSource, HoverTool, Toggle
from bokeh.layouts import layout
from bokeh.transform import dodge
from bokeh.resources import CDN
from bokeh.embed import file_html

#Open file:
def open_tsv(filename):
    df = pd.read_csv(filename, na_values='inf', sep='\t')

    if len(df.columns) > 7:
        df = pd.read_csv(filename, usecols=list(range(0, 7)), na_values='inf', sep='\t',header=0, index_col=False)
        df.columns=['Substrate','Control_mean','Inhibitor_mean','Fold_change','p_value','ctrlCV','treatCV']
        return df
    elif len(df.columns) < 7:
        df = pd.read_csv(filename, na_values='inf', sep='\t')
        df.columns = ["Substrate", "Control_mean", "Inhibitor_mean", "Fold_change", "p_value"]
        return df
    else: #len(df.columns)== 7
        df = pd.read_csv(filename, na_values='inf', sep='\t')
        df.columns=['Substrate','Control_mean','Inhibitor_mean','Fold_change','p_value','ctrlCV','treatCV']
        return df

#Filter data:
def initial_data_filter(df):
    if len(df.columns)== 7:
        df=df.fillna({'ctrlCV':0, 'treatCV':0}) #replace NaN in variance columns with 0
        df=df.dropna(axis='index', how='any')
        df=df[~df.Substrate.str.contains("None")]
        M= r"\([M]\d+\)" #matches M in brackets with one or more digits
        df=df[~df.Substrate.str.contains(M)] #drops rows with M residue
        phos=df.Substrate.str.findall(r"\((.\d+)").apply(','.join, 1)
        df.insert(1, "Phosphosite", phos, True) #inserts phosphosite data as the second column
        df[["Substrate"]]=df.Substrate.str.extract(r"(.+)\(")
        return df
    else:
        df=df.dropna(axis='index', how='any')
        df=df[~df.Substrate.str.contains("None")]
        M= r"\([M]\d+\)" #matches M in brackets with one or more digits
        df=df[~df.Substrate.str.contains(M)] #drops rows with M residue
        phos=df.Substrate.str.findall(r"\((.\d+)").apply(','.join, 1)
        df.insert(1, "Phosphosite", phos, True) #inserts phosphosite data as the second column
        df[["Substrate"]]=df.Substrate.str.extract(r"(.+)\(")
        return df

#Find substrate gene name from uniprot API
def find_sub_gene(entry):
     if re.match(r".+_HUMAN", entry):
        URL = 'http://www.uniprot.org/uniprot/?query==mnemonic:'+entry+'&columns=genes(PREFERRED)&format=tab'
        r = requests.get(URL)
        content = r.text.splitlines()
        gene_name=content[1:2]        
        return str(gene_name)  #returns gene as a string
     else:
        return entry           #if entry doesn't match regex, return the entry (gene name)

def convert_to_gene(df):
    df.Substrate=df.apply(lambda row: find_sub_gene(row["Substrate"]), axis=1)
    df.Substrate=df.Substrate.str.strip("[]").str.strip("''") #remove [] and ''
    df.Substrate.replace("", np.nan, inplace=True)
    df.dropna(subset=["Substrate"], inplace=True)
    return df

def find_kinase(df):
    #Find Kin_Gene_Name from Substrate_Gene_Name and Substrate_Modified_Residue
    conn = sqlite3.connect("Database.db") #connect to our database
    phosdf=pd.read_sql_query('SELECT KINASE_GENE_NAME, SUB_GENE_NAME, SUB_MOD_RSD FROM PhosphoSites', conn) 
    df1= df.join(phosdf.set_index(['SUB_GENE_NAME', 'SUB_MOD_RSD']), on =['Substrate', 'Phosphosite'])
    #join database dataframe with file dataframe where substrate gene name and modified residue are the index
    df1= df1.rename(columns={'KINASE_GENE_NAME': 'Kinase'})
    volplot_table=df1.to_csv('./static/volplot_table.csv', sep=',')
    return df1 #returns dataframe with Kinases (NaN results included)
    return volplot_table #returns dataframe as csv

def relative_kinase_activity(df1):
    #Find relative kinase activity
    kinase_sum= df1.groupby("Kinase").Control_mean.sum() #sum of each kinase
    total_sum=df1.Control_mean.sum() #total sum of kinases in the file
    Relative_Kinase_Activity=kinase_sum/total_sum
    #Relative kinase activity of inhibitor
    inhib_sum= df1.groupby("Kinase").Inhibitor_mean.sum() #sum of means for inhibitor data
    inhib_total=df1.Inhibitor_mean.sum()
    inhib_activity=inhib_sum/inhib_total
    kinasedf=pd.DataFrame({"Control_Mean":kinase_sum, "Relative_Kinase_Activity":Relative_Kinase_Activity, 
                       "Relative_Inhibited_Kinase_Activity":inhib_activity, "Inhibitor_Mean":inhib_sum})
    kinasedf = kinasedf.reset_index()
    kinasedf=kinasedf.sort_values(by='Relative_Kinase_Activity', ascending=False) #sort data by descending control mean value
    barplot_table=kinasedf.to_csv('./static/barplot_table.csv')
    return kinasedf #returns sorted dataframe
    return barplot_table #returns sorted dataframe as csv

def rka_barchart(kinasedf):
    #Bar graph of Relative Kinase Activity
    kinase_name=kinasedf.Kinase[0:25] #Top 25 Kinases
    src=ColumnDataSource(kinasedf)
    hover=HoverTool(tooltips=[('Kinase','@Kinase'), ('Relative Kinase Activity', '@Relative_Kinase_Activity'),
                          ('Relative Inhibited Kinase Activity','@Relative_Inhibited_Kinase_Activity')])
    plot1=figure(y_range=kinase_name, plot_height=1800)
    #plot1.title.text="Relative Kinase Activity of the Top 25 Identified Kinases"
    plot1.title.text_font_size = "15px"
    plot1.xaxis.axis_label ="Relative Kinase Activity (AU)"
    plot1.x_range.start = 0
    plot1.yaxis.axis_label="Kinase"
    plot1.hbar(y=dodge('Kinase',-0.25, range=plot1.y_range), right='Relative_Kinase_Activity', height=0.45, source=src, color='#2F4F4F', legend='Relative Kinase Activity')
    plot1.hbar(y=dodge('Kinase',0.25, range=plot1.y_range), right='Relative_Inhibited_Kinase_Activity', height=0.45, source=src, color="#e84d60", legend='Relative Inhibited Kinase Activity')
    plot1.add_tools(hover)
    return plot1

def volplot_1(df1):
    #Data for volcano plot:
    df1 = df1[df1.Fold_change != 0] #remove rows where fold change is 0
    df1["Log_Fold_change"]=np.log2(df1["Fold_change"])
    df1["Log_p_value"]=-np.log10(df1["p_value"])
    #Volcano plot 1:
    source=ColumnDataSource(df1)
    vol_hover=HoverTool(tooltips=[('Kinase','@Kinase'), ('Substrate', '@Substrate'),
                             ('Modified Residue','@Phosphosite'), ('Fold Change','@Fold_change'), ('p-value', '@p_value')])
    p = figure(plot_width=700, plot_height=500)
    #p.title.text="Volcano Plot of the Log Fold Change and Log p-value for Complete Protein"
    p.title.text_font_size = "15px"
    p.xaxis.axis_label ="Log Fold Change"
    p.yaxis.axis_label ="-Log p-value"
    p.scatter(x='Log_Fold_change', y='Log_p_value', source=source)
    p.add_tools(vol_hover)
    #Significance thresholds:
    sig5=Span(location=1.3, dimension='width', line_color='#800000', line_width=1.75, line_dash='dashed') #5%
    sig1=Span(location=2, dimension='width', line_color='#2F4F4F', line_width=1.75, line_dash='dashed') #1%
    toggle1=Toggle(label='1% Significance', button_type="success", active=True)
    toggle1.js_link('active', sig1, 'visible')
    toggle2=Toggle(label='5% Significance', button_type="success", active=True)
    toggle2.js_link('active', sig5, 'visible')
    p.add_layout(sig1) #adds horizontal line where points below line are non-sig fold changes(-log(0.01)=2.0)
    p.add_layout(sig5) #adds horizontal line where points below line are non-sig fold changes(-log(0.05)=1.3)
    plot2=layout([p], [toggle1, toggle2])
    return plot2

def volplot_2(df1):
    #Data for volcano plot 2:
    df1=df1.dropna(how='any')
    df1 = df1[df1.Fold_change != 0] #remove rows where fold change is 0
    df1["Log_Fold_change"]=np.log2(df1["Fold_change"])
    df1["Log_p_value"]=-np.log10(df1["p_value"])
    #Volcano plot 2:
    source=ColumnDataSource(df1)
    vol_hover=HoverTool(tooltips=[('Kinase','@Kinase'), ('Substrate', '@Substrate'),
                                 ('Modified Residue','@Phosphosite'), ('Fold Change','@Fold_change'), ('p-value', '@p_value')])
    p2 = figure(plot_width=700, plot_height=500)
    #p2.title.text="Volcano Plot of the Log Fold Change and Log p-value for All Identified Kinases"
    p2.title.text_font_size = "15px"
    p2.xaxis.axis_label ="Log Fold Change"
    p2.yaxis.axis_label ="-Log p-value"
    p2.scatter(x='Log_Fold_change', y='Log_p_value', source=source)
    p2.add_tools(vol_hover)
    #Significance thresholds:
    sig5=Span(location=1.3, dimension='width', line_color='#800000', line_width=1.75, line_dash='dashed') #5%
    sig1=Span(location=2, dimension='width', line_color='#2F4F4F', line_width=1.75, line_dash='dashed') #1%
    toggle1=Toggle(label='1% Significance', button_type="success", active=True)
    toggle1.js_link('active', sig1, 'visible')
    toggle2=Toggle(label='5% Significance', button_type="success", active=True)
    toggle2.js_link('active', sig5, 'visible')
    p2.add_layout(sig1) #adds horizontal line where points below line are non-sig fold changes(-log(0.01)=2.0)
    p2.add_layout(sig5) #adds horizontal line where points below line are non-sig fold changes(-log(0.05)=1.3)
    plot3=layout([p2], [toggle1, toggle2])
    return plot3

#Embedding
#html =file_html(p, CDN)
