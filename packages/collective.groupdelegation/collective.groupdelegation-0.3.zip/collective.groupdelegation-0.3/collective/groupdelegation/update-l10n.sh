#i18ndude rebuild-pot --pot i18n/collective.groupdelegation-plone.pot --create plone --merge i18n/collective.groupdelegation-plone-manual.pot profiles
#i18ndude filter i18n/collective.groupdelegation-plone.pot ~/.buildout/eggs/plone.app.locales*/plone/app/locales/i18n/plone.pot > i18n/collective.groupdelegation-plone.pot_
#mv i18n/collective.groupdelegation-plone.pot_ i18n/collective.groupdelegation-plone.pot
#i18ndude sync --pot i18n/collective.groupdelegation-plone.pot i18n/collective.groupdelegation-plone-??.po
i18ndude sync --pot i18n/collective.groupdelegation-plone-manual.pot i18n/collective.groupdelegation-plone-??.po

i18ndude rebuild-pot --pot i18n/collective.groupdelegation.pot --create collective.groupdelegation .
i18ndude sync --pot i18n/collective.groupdelegation.pot i18n/collective.groupdelegation-??.po
