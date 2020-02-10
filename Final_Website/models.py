from application import db

class Kinase(db.Model):
    __tablename__ = 'Kinase'
    Kinase_Gene_Name = db.Column('Kinase_Gene_Name', db.String)
    Kinase_Protein_Name = db.Column('Kinase_Protein_Name', db.String)
    Kinase_Group = db.Column('Kinase_Group', db.String)
    Family = db.Column('Family', db.String)
    SubFamily = db.Column('SubFamily', db.String)
    UniProt_ID = db.Column('UniProt_ID', db.String, primary_key = True)
    UniProt_Entry = db.Column('UniProt_Entry', db.String)
    Alias = db.Column('Alias', db.String)
    Subcellular_Location = db.Column('Subcellular_Location', db.String)

class Phosphosite(db.Model):
	__tablename__ = 'PhosphoSites'
	PHOSPHO_ID = db.Column('PHOSPHO_ID', db.Integer, primary_key = True)
	KINASE_GENE_NAME = db.Column('KINASE_GENE_NAME', db.String)
	KIN_UNIPROT_ID = db.Column('KIN_UNIPROT_ID', db.String)
	SUBSTRATE_NAME = db.Column('SUBSTRATE_NAME', db.String)
	SUB_UNIPROT_ID = db.Column('SUB_UNIPROT_ID', db.String)
	SUB_GENE_NAME = db.Column('SUB_GENE_NAME', db.String)
	SUB_MOD_RSD = db.Column('SUB_MOD_RSD', db.String)
	SITE_7_AA = db.Column('SITE_7_AA', db.String)
	CHR_LOC = db.Column('CHR_LOC', db.String)
	SUB_ENTRY_NAME = db.Column('SUB_ENTRY_NAME', db.String)

class Inhibitors(db.Model):
    __tablename__ = 'Inhibitors'
    INHIBITOR_ID = db.Column('INHIBITOR_ID', db.Integer, primary_key = True)
    INN_Name = db.Column('INN_Name', db.String)								
    Targets = db.Column('Targets', db.String)
    RoF = db.Column('RoF', db.Integer)
    MW = db.Column('MW', db.Integer)
    LogP = db.Column('LogP', db.Integer)
    TPSA = db.Column('TPSA', db.Integer)
    HBA = db.Column('HBA', db.Integer)
    HBD = db.Column('HBD', db.Integer)
    NRB = db.Column('NRB', db.Integer)
    Smiles = db.Column('Smiles', db.String)
    InChi_Key = db.Column('InChi_Key', db.String)
    ChEMBL_ID = db.Column('ChEMBL_ID', db.String)
    image_link = db.Column('image_link', db.String)

class Kin_Pho_Interaction(db.Model):
    __tablename__ = 'Kin_Pho_Interaction'
    KinPhoID = db.Column('KinPhoID', db.Integer, primary_key = True)
    Kin = db.Column('Kin', db.String)
    Pho = db.Column('Pho', db.Integer)

class Kin_Inh_Interaction(db.Model):
    __tablename__ = 'Kin_Inh_Interaction'
    InteractionID = db.Column('InteractionID', db.Integer, primary_key = True)
    Kina = db.Column('Kina', db.String)
    Inhi = db.Column('Inhi', db.Integer)
