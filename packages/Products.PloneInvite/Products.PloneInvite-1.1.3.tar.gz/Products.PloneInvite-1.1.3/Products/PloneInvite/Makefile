I18N_DOMAIN = PloneInvite

default:
	@echo "Nothing to do by default."
	@echo "Use 'make pot' to create or update .pot from skins directory."
	@echo "Use 'make xx.po' to create or update translation file from .pot, where xx is your language."

# Create or update a {i18ndomain}.pot file
pot:
	touch i18n/${I18N_DOMAIN}.pot
	# Back up the existing file
	cp i18n/${I18N_DOMAIN}.pot i18n/${I18N_DOMAIN}.pot.backup
	i18ndude rebuild-pot --pot i18n/${I18N_DOMAIN}.pot \
		--create ${I18N_DOMAIN} skins/ploneinvite/
	i18ndude merge --pot i18n/${I18N_DOMAIN}.pot	--merge i18n/base.pot

# Update translation files {i18ndomain}-{xx}.pot
# and plone-{xx}.pot, creating them if needed.
%.po: pot
	touch i18n/${I18N_DOMAIN}-$*.po
	# Back up the existing file
	cp i18n/${I18N_DOMAIN}-$*.po i18n/${I18N_DOMAIN}-$*.po.backup
	i18ndude sync --pot i18n/${I18N_DOMAIN}.pot i18n/${I18N_DOMAIN}-$*.po
	# And for the plone domain translations, too.
	touch i18n/plone-$*.po
	cp i18n/plone-$*.po i18n/plone-$*.po.backup
	# Note that we assume that there's a 'plone.pot' file in 'i18n/'.
	i18ndude sync --pot i18n/plone.pot i18n/plone-$*.po
