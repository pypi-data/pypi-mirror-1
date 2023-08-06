from sqlalchemy import create_engine
#engine = create_engine('sqlite:///:memory:', echo=True)
#engine = create_engine('postgres://username:password@hostname:port/databasename', echo=True)
#engine = create_engine('postgres://username:password@hostname:port/databasename', echo=True)
#engine = create_engine('mysql://username:password@hostname:port/databasename', echo=True)
#engine = create_engine('sqlite:///./devdata.db', echo=True)
engine = create_engine('mysql://lm:tilmsite@localhost/lm', echo=True)

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import sqlalchemy

#engine.echo=True
engine.echo=False
metadata=sqlalchemy.MetaData(engine)

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper

#Session = sessionmaker(bind=engine, autoflush=True, autocommit=True)
Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
session = Session()

#Connected to a database
#log.info("Connected to a Database")

#class Recall(object):
#    pass

#python class
class Recall(object):
    def __init__(self, **kw):
        for key,value in kw.items():
            setattr(self, key, value)

from datetime import datetime
import time

#Data from RCL.txt
#The RECALL file contains all NHTSA safety-related defect and compliance campaigns since 1967.
#Maximum Record length: 8759
#Change log:
#1.Field# 23 added as of Sept. 14, 2007
#2.Changed flat file extension from .lst to .txt as of Sept. 14, 2007
#3.Field# 24 added as of March 14, 2008
#Last Updated March 14, 2008


recall_table = sqlalchemy.Table('recall_db', metadata,
    sqlalchemy.Column('RECORD_ID', sqlalchemy.Integer, primary_key=True,info={"description":"RUNNING SEQUENCE NUMBER,WHICH UNIQUELY IDENTIFIES THE RECORD."}),
    sqlalchemy.Column('CAMPNO', sqlalchemy.String(12),info={"description":"NHTSA CAMPAIGN NUMBER"}),
    sqlalchemy.Column('MAKETXT', sqlalchemy.String(25),info={"description":"VEHICLE/EQUIPMENT MAKE"}),
    sqlalchemy.Column('MODELTXT', sqlalchemy.String(255),info={"description":"VEHICLE/EQUIPMENT MODEL"}),
    sqlalchemy.Column('YEARTXT', sqlalchemy.String(4),info={"description":"MODEL YEAR, 9999 IF UNKNOWN or N/A"}),
    sqlalchemy.Column('MFGCAMPNO', sqlalchemy.String(20),info={"description":"MFR CAMPAIGN NUMBER"}),
    sqlalchemy.Column('COMPNAME', sqlalchemy.String(255),info={"description":"COMPONENT DESCRIPTION"}),
    sqlalchemy.Column('MFGTXT', sqlalchemy.String(40),info={"description":"MANUFACTURER THAT FILED DEFECT/NONCOMPLIANCE REPORT"}),
    sqlalchemy.Column('BGMAN', sqlalchemy.String(8), info={"description":"BEGIN DATE OF MANUFACTURING"}),
    sqlalchemy.Column('ENDMAN', sqlalchemy.String(8), info={"description":"END DATE OF MANUFACTURING"}),
    sqlalchemy.Column('RCLTYPECD', sqlalchemy.String(4),info={"description":"VEHICLE, EQUIPMENT OR TIRE REPORT"}),
    sqlalchemy.Column('POTAFF', sqlalchemy.String(9),info={"description":"POTENTIAL NUMBER OF UNITS AFFECTED"}),
    sqlalchemy.Column('ODATE', sqlalchemy.String(8),info={"description":"DATE OWNER NOTIFIED BY MFR"}),
    sqlalchemy.Column('INFLUENCED_BY', sqlalchemy.String(4),info={"description":"RECALL INITIATOR (MFG/OVSC/ODI)"}),
    sqlalchemy.Column('MFGNAME', sqlalchemy.String(40),info={"description":"MANUFACTURERS OF RECALLED VEHICLES/PRODUCTS"}),
    sqlalchemy.Column('RCDATE', sqlalchemy.String(8),info={"description":"REPORT RECEIVED DATE"}),
    sqlalchemy.Column('DATEA', sqlalchemy.String(8),info={"description":"RECORD CREATION DATE"}),
    sqlalchemy.Column('RPNO', sqlalchemy.String(3),info={"description":"REGULATION PART NUMBER"}),
    sqlalchemy.Column('FMVSS', sqlalchemy.String(10),info={"description":"FEDERAL MOTOR VEHICLE SAFETY STANDARD NUMBER"}),
    sqlalchemy.Column('DESC_DEFECT', sqlalchemy.Text,info={"description":"DEFECT SUMMARY"}),
    sqlalchemy.Column('CONEQUENCE_DEFECT', sqlalchemy.Text,info={"description":"CONSEQUENCE SUMMARY"}),
    sqlalchemy.Column('CORRECTIVE_ACTION', sqlalchemy.Text,info={"description":"CORRECTIVE SUMMARY"}),
    sqlalchemy.Column('NOTES', sqlalchemy.Text,info={"description":"RECALL NOTES"}),
    sqlalchemy.Column('RCL_CMPT_ID', sqlalchemy.String(27),info={"description":"NUMBER THAT UNIQUELY IDENTIFIES A RECALLED COMPONENT."}),
    )
#Dropping an existing table if exists
metadata.drop_all(engine)

#Create table structure
metadata.create_all(engine)
mapper(Recall,recall_table)
session.flush()


#Start loading your data below
#fill recall database from a tsv
import csv
reader = csv.reader(open("../parse/FLAT_RCL.txt"),delimiter="\t")

#We are going to loop through file and add the data to database.
j=0
for RECORD_ID,CAMPNO,MAKETXT,MODELTXT,YEARTXT,MFGCAMPNO,COMPNAME,MFGTXT,BGMAN,ENDMAN,RCLTYPECD,POTAFF,ODATE,INFLUENCED_BY,MFGNAME,RCDATE,DATEA,RPNO,FMVSS,DESC_DEFECT,CONEQUENCE_DEFECT,CORRECTIVE_ACTION,NOTES,RCL_CMPT_ID in reader:
    #print RECORD_ID,CAMPNO,MAKETXT,MODELTXT,YEARTXT,MFGCAMPNO,COMPNAME,MFGTXT,BGMAN,ENDMAN,RCLTYPECD,POTAFF,ODATE,INFLUENCED_BY,MFGNAME,RCDATE,DATEA,RPNO,FMVSS,DESC_DEFECT,CONEQUENCE_DEFECT,CORRECTIVE_ACTION,NOTES,RCL_CMPT_ID
    #This creates a Recall row, and fills it in with data from csv.
    record=Recall(RECORD_ID=RECORD_ID,CAMPNO=CAMPNO,MAKETXT=MAKETXT,MODELTXT=MODELTXT,YEARTXT=YEARTXT,MFGCAMPNO=MFGCAMPNO,COMPNAME=COMPNAME,MFGTXT=MFGTXT,BGMAN=BGMAN,ENDMAN=ENDMAN,RCLTYPECD=RCLTYPECD,POTAFF=POTAFF,ODATE=ODATE,INFLUENCED_BY=INFLUENCED_BY,MFGNAME=MFGNAME,RCDATE=RCDATE,DATEA=DATEA,RPNO=RPNO,FMVSS=FMVSS,DESC_DEFECT=DESC_DEFECT,CONEQUENCE_DEFECT=CONEQUENCE_DEFECT,CORRECTIVE_ACTION=CORRECTIVE_ACTION,NOTES=NOTES,RCL_CMPT_ID=RCL_CMPT_ID)
    #This adds it to the session.    
    session.add(record)
    j+=1
    if j%10000==0:
        print 'saving %dth row' %j
        #Saving to db every 10,000 records
        session.flush()
session.commit()
print 'Commiting All Changes'


y=session.query(Recall).limit(5).all()
for i in y:
    print 'Getting 5 records'
    print  i.YEARTXT,i.MAKETXT,i.MODELTXT,i.COMPNAME
