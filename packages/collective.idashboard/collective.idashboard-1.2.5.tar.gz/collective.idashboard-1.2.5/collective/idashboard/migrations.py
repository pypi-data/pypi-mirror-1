
def run_all_import_steps(portal_setup):
    """This example invokes an extension profile which in turn performs
    a migration.
    """
    portal_setup.runAllImportStepsFromProfile('profile-collective.idashboard:default', 
                                               purge_old=False)
