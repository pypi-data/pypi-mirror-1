try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

PROJECTNAME = "rcom.pas.gapps"
PACKAGENAME = PROJECTNAME
DEPENDENCIES = []

GLOBALS = globals()
