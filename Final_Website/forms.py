from wtforms import Form, StringField, SelectField
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from wtforms import validators

# Create search forms for the three searches on the site
class KinaseSearchForm(Form):
    choices = [('Kinase Gene Name','Kinase Gene Name'), ('Kinase Uniprot ID','Kinase Uniprot ID'),('Alias Name','Alias Name')] # Define choices for the kinase search
    select = SelectField('Kinase Search:', choices=choices) # the select field will include the choices defined
    search = StringField('',[validators.DataRequired()]) # this is a field that is empty that allows the user to search - a data required validator is added.

class InhibitorSearchForm(Form):
    choices = [('Inhibitor ChEMBL ID','Inhibitor ChEMBL ID'), ('Inhibitor Name','Inhibitor Name'), ('Targets','Targets')]
    select = SelectField('Inhibitor Search:', choices=choices)# Define choices for the inhibitor search
    search = StringField('',[validators.DataRequired()])# this is a field that is empty that allows the user to search - a data required validator is added.

class PhosphositeSearchForm(Form):
    choices = [('Substrate Gene Name','Substrate Gene Name'), ('Substrate Uniprot ID','Substrate Uniprot ID'), ('Substrate Name','Substrate Name')]# Define choices for the phosphosite search
    select = SelectField('Phosphosite Search:', choices=choices)
    search = StringField('',[validators.DataRequired()])# this is a field that is empty that allows the user to search - a data required validator is added.

