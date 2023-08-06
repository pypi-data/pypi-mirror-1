from django.db.models.signals import post_syncdb
from django.db import connection
import settings

LINKABLE = getattr(settings, 'LINKABLE_MODELS', {})

def updateLinkTable(sender, **kwargs):
    for k,v in LINKABLE.iteritems():    
    #create columns for any relationships that don't already exist
    #not currently putting in fk constraints, just adding the column.
        column = v.split(".")[-1] + "_id"
        try:
            cursor = connection.cursor()
            sql = "SELECT " +column+ " from links_link"
            cursor.execute(sql)
        except:
            print "creating column now"
            cursor = connection.cursor()
                    
            #ALTER TABLE links_link ADD COLUMN apartment_id INTEGER DEFAULT NULL;
            table = v.replace(".", "_")
            constraint = table + "_fk"
            print table
            sql = """ALTER TABLE links_link ADD COLUMN """+column+""" INTEGER DEFAULT NULL;"""
#                  ALTER TABLE links_link ADD CONSTRAINT """+constraint+ """ FOREIGN KEY ("""+column+""")
#                  REFERENCES """ +table+""" (id);
#            """
            cursor.execute(sql)

#listen for syncdb signal
post_syncdb.connect(updateLinkTable)
