collective.blueprint.translationlinker
======================================

A transmogrifier blueprint to create links between content items to mark them
as Products.LinguaPlone translations of each other.

Variables in the blueprint include:

`_canonicalTranslation`
    Boolean saying whether the item is the canonical translation.

`_translationOf`
    Path to the canonical object.

`language`
    The default field of translatable content containing the language code
    of the language of the object.

