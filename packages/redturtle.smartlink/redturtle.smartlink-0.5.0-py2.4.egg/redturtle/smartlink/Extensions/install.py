def install(portal):
    setup_tool = portal.portal_setup
    setup_tool.setImportContext('profile-redturtle.smartlink:default')
    setup_tool.runAllImportSteps()

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.setImportContext('profile-redturtle.smartlink:uninstall')
        setup_tool.runAllImportSteps()
