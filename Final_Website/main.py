### Import required packages!
import os
from application import application
from flask import Flask, Markup, render_template, flash,url_for, render_template, request, redirect,g,send_from_directory, Response, request, send_file
from forms import KinaseSearchForm, PhosphositeSearchForm, InhibitorSearchForm
from models import Kinase, Phosphosite, Inhibitors
from db_setup import init_db, db_session
import pandas as pd
import numpy as np
import requests
from werkzeug.utils import secure_filename
from bokeh.plotting import figure, show
from bokeh.models import Span, ColumnDataSource, HoverTool, Toggle
from bokeh.layouts import layout
from bokeh.transform import dodge
from bokeh.resources import CDN
from bokeh.embed import file_html, components

###############################################################################


init_db() #initialise the database

###############################################################################
@application.route("/") #define homepage route
def home():
  return render_template("layout.html")

#
@application.route("/about_us")
def about_us():
    return render_template("about.html")

#
@application.route("/contact_us")
def contact_us():
    return render_template("contact.html")
#
@application.route("/help")
def help():
    return render_template("help.html")

###### Kinase #################################################################
@application.route('/kinase', methods=['GET', 'POST'])
def kinase():
    search = KinaseSearchForm(request.form) # import search form and run a request
    if request.method == 'POST': # if the user is searching for information (ie posting a searchstring to retrieve data)
        return Kinase_search_results(search) # run the kinase search function
    return render_template('kinase.html', form=search)

@application.route('/Kinase_search_results')
def Kinase_search_results(search):
    results = []
    search_string = search.data['search'] # search string given the user input data
    if search_string:
        if search.data['select'] == 'Kinase Gene Name': # check if protein kinase name was selected
            qry = db_session.query(Kinase).filter(Kinase.Kinase_Gene_Name.contains(search_string))
            results = qry.all() # output all the query results
            iqry = db_session.query(Kinase, Inhibitors)\
            .filter(Inhibitors.Targets.contains(search_string))\
            .join(Kinase, Inhibitors.Targets.contains(search_string) == Kinase.Kinase_Gene_Name.contains(search_string))
            inhibresults = iqry.all()
            pqry = db_session.query(Kinase, Phosphosite)\
            .filter(Kinase.Kinase_Gene_Name.contains(search_string))\
            .join(Phosphosite, Kinase.Kinase_Gene_Name.contains(search_string) == Phosphosite.KINASE_GENE_NAME.contains(search_string))
            phosphresults = pqry.all() # run a join query to find out kinase substrates
        elif search.data['select'] == 'Kinase Uniprot ID': # check if uniprot id was selected
            qry = db_session.query(Kinase).filter(Kinase.UniProt_ID.ilike(search_string))
            results = qry.all()
            iqry = db_session.query(Kinase, Inhibitors)\
            .filter(Kinase.UniProt_ID.contains(search_string))\
            .join(Inhibitors, Kinase.Kinase_Gene_Name == Inhibitors.Targets)
            inhibresults = iqry.all()
            pqry = db_session.query(Kinase, Phosphosite)\
            .filter(Kinase.UniProt_ID.contains(search_string))\
            .join(Phosphosite, Kinase.Kinase_Gene_Name == Phosphosite.KINASE_GENE_NAME.ilike(search_string))
            phosphresults = pqry.all() # run a join query to find out kinase substrates
        elif search.data['select'] == 'Alias Name': # check if alias name was selected #search_string = search_string.upper()
            kinase = db_session.query(Kinase).filter(Kinase.Alias.contains(search_string)) # query alias name
            qry = db_session.query(Kinase).filter(Kinase.Alias.contains(search_string))
            results = qry.all() # output all the query results
            iqry = db_session.query(Kinase, Inhibitors)\
            .filter(Kinase.Alias.contains(search_string))\
            .join(Inhibitors, Kinase.Alias.contains(search_string) == Inhibitors.Targets.contains(search_string))
            inhibresults = iqry.all()
            pqry = db_session.query(Kinase, Phosphosite)\
            .filter(Kinase.Alias.contains(search_string))\
            .join(Phosphosite, Kinase.Alias.contains(search_string) == Phosphosite.KINASE_GENE_NAME.ilike(search_string))
            phosphresults = pqry.all() # run a join query to find out kinase substrates
    if not results: # if no results were found
        flash('No results found!') #flash the error message
        return redirect('/kinase') # and return back to kinase search
    else:
        return render_template("kinase_search_results.html", results=results, inhibresults=inhibresults, phosphresults=phosphresults)


@application.route('/kinase/<kinase>') # for the internal hyperlink a kinase profile route is defined, and the <kinase> is queried as before.
def kinaseprofile(kinase):
    qry = db_session.query(Kinase).filter(Kinase.Kinase_Gene_Name.contains(kinase))
    results = qry.all()
    return render_template('kinase_Search.html', results=results)# render the kinase results page

###### Inhbitor ###############################################################
@application.route('/Inhibitor', methods=['GET', 'POST'])
def Inhibitor():
    search = InhibitorSearchForm(request.form)
    if request.method == 'POST':
        return inhibitor_search_results(search)# run the inhibitor search function if the method is POST
    return render_template('Inhibitor.html', form=search)

@application.route('/inhibitor_search_results')
def inhibitor_search_results(search):
    results = []
    search_string = search.data['search'] # search string given the user input data   
    if search_string:
        if search.data['select'] == 'Inhibitor ChEMBL ID':
            qry = db_session.query(Inhibitors).filter(Inhibitors.ChEMBL_ID.contains(search_string)) # search for chembl ID that is
            # same as the search string - use ilike for case sensitive search
            results = qry.all()
        elif search.data['select'] == 'Inhibitor Name':
            qry = db_session.query(Inhibitors).filter(Inhibitors.INN_Name.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Targets':
            qry = db_session.query(Inhibitors).filter(Inhibitors.Targets.contains(search_string))
            results = qry.all()
    if not results:
        flash('No results found!')
        return redirect('/Inhibitor')
    else:
        # display results
        return render_template("inhibitor_search_results.html", results=results)

@application.route('/Inhibitor/<INN_Name>') # for the internal hyperlink an inhibitor profile route is defined.
def inhib_INN_Name_profile(INN_Name):
    qry = db_session.query(Inhibitors).filter(Inhibitors.INHIBITOR_ID.ilike(INN_Name))
    results = qry.all()
    return render_template('inhibitor_search.html', results=results) # render the inhibitor results page

###### Phosphosites ###########################################################
@application.route('/Phosphosites', methods=['GET', 'POST'])
def Phosphosites():
    search = PhosphositeSearchForm(request.form)
    if request.method == 'POST':
        return phosphosite_search_results(search)# run the phosphosite search function if the method is POST
    return render_template('Phosphosite.html', form=search)

@application.route('/phosphosite_search_results')
def phosphosite_search_results(search):
    results = []
    search_string = search.data['search']
    if search_string:
        if search.data['select'] == 'Substrate Gene Name':
            qry = db_session.query(Phosphosite).filter(Phosphosite.SUB_GENE_NAME.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Substrate Uniprot ID':
            qry = db_session.query(Phosphosite).filter(Phosphosite.SUB_UNIPROT_ID.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Substrate Name':
            qry = db_session.query(Phosphosite).filter(Phosphosite.SUBSTRATE_NAME.contains(search_string))
            results = qry.all()
    if not results:
        flash('No results found!')
        return redirect('/Phosphosites')
    else:
        return render_template("phosphosite_search_results.html", results=results)

@application.route('/substrate/<Substrate>') # for the internal hyperlink a substrate profile route is defined.
def substrateprofile(Substrate):
    qry = db_session.query(Phosphosite).filter(Phosphosite.PHOSPHO_ID.ilike(Substrate))
    results = qry.all()
    return render_template('phosphosite_search.html', results=results) # render the inhibitor results page

###############################################################################
###TOOLS ###
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))

ALLOWED_EXTENSIONS= set(['tsv'])   #only tsv files are allowed

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application.route("/Tool/", methods=['GET','POST'])
def Tool():
    return render_template('data_upload.html')      #The upload button is shown


@application.route('/Tool/data_file_results', methods=['GET','POST'])
def data_file_results():  
    target = os.path.join(UPLOAD_FOLDER, 'static/')    #to create a folder into which the file will be saved
    print(target)
    if not os.path.isdir(target):                  #if folder is not made it should be made
        os.mkdir(target)
    for file in request.files.getlist("file"):
        filename = secure_filename(file.filename)
        print(file)
        filename =file.filename
        destination ="/".join([target, "temp.tsv"])   #saves teh file as temp.tsv
        print(destination)
        file.save(destination) 
     
    filename="./static/temp.tsv"
    import data_visualisation
    ##### UPDATE WITH SAMIA SCRIPT #############
    df = data_visualisation.open_tsv(filename)
    data = data_visualisation.initial_data_filter(df)
    substrate = data_visualisation.convert_to_gene(data)
    kinase = data_visualisation.find_kinase(substrate)
    rka = data_visualisation.relative_kinase_activity(kinase)
    barplot = data_visualisation.rka_barchart(rka)
    html =file_html(barplot, CDN)
    volcano_plot1 = data_visualisation.volplot_1(kinase)
    html_1 = file_html(volcano_plot1, CDN)
    volcano_plot2 = data_visualisation.volplot_2(kinase)
    html_2 = file_html(volcano_plot2, CDN)

###To get he java script of the Bokeh volcano plot, to ensure the link is dynamic and changes with the newer version of Bokeh that's why these are added here
     #CDN: Content Delivery Network

    cdn_js=CDN.js_files[0:]

    #To get the CSS style sheet of the Bokeh volcano plot
    cdn_css=CDN.css_files[0:]


    return render_template("phosphoproteomics_result.html",
	html=html,
	html_1=html_1,
        html_2=html_2,
        cdn_css=cdn_css,
        cdn_js=cdn_js)


###############################
if __name__ == "__main__":
  application.run(debug=True)
