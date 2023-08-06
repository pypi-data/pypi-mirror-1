How to add msgids?

--> add them to the collective.facetednavigation.pot (collective.facetednavigation domain) or collective.facetednavigation-plone.pot (plone domain) files.
    --> Also can uses i18ndude for rebuild pot file into dev collective.facetednavigation dir 
running the below command "i18ndude rebuild-pot --pot locales/the_pot_file --create domain ./"
--> run "i18ndude sync --pot the_pot_file the_po_file_to_be_updated"
--> translate the new msgids

How to create a new language translation file?

--> run "i18ndude sync --pot the_pot_file the_new_po_file"
--> modify the first msgstr of the freshly created .po file
    --> define a correct "Language-Code: \n" and a correct "Language-Name: \n"
