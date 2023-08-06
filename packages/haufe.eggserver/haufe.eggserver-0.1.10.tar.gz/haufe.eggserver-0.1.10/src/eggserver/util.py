##########################################################################
# haufe.eggserver
# (C) 2008, Haufe Mediengruppe Freiburg, ZOPYX Ltd. & Co. KG
# Written by Andreas Jung
# Published under the Zope Public License V 2.1
##########################################################################


def toUnicode(s):
    """ Convert a string to unicode by guessing """

    try:
        return unicode(s, 'iso-8859-15')
    except UnicodeDecodeError:
        return unicode(s, 'utf-8')
