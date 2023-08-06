################################################################
# zopyx.multieventcalendar
#
# (C) 2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('zopyx.multieventcalendar_various.txt') is None:
        return

    # Add additional setup code here
