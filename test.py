import driver_init
from web.xpaths import XpathResolver

driver_init.BrowserDriver().browser.get('E:/Downloads/NSH_templates/type_1/init_state.mhtml')

XpathResolver().iframe()
