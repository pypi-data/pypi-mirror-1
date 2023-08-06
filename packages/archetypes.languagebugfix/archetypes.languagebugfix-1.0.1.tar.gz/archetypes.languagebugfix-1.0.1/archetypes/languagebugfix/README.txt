Archetypes Language Field Bug Fix
=================================

Introduction
------------

    archetypes.languagebugfix package aims to fix an `issue 
    <https://dev.plone.org/plone/ticket/8907>`_ with the default vocabulary for 
    ExtensibleMetadata language field in Archetypes.

    This issue affects only contents created in languages which code are in 
    the form lc-cc(lc, language code; cc, contry code) and its effects appear when 
    you have a Lingua Plone installation and a combined language code is used as 
    default language for the site -- translations losing their reference to canonical 
    versions of the content.

    Keep in mind this package is to be used until an Archetypes version with the 
    proper fix is released, so, probably there won't be another release.

Testing the issue
-----------------

    Let's setup our basic test variables::

        >>> from Products.CMFPlone.utils import getToolByName
        >>> self.loginAsPortalOwner()
        >>> portal = self.portal
        >>> lt = getToolByName(portal,'portal_languages')
        >>> pp = getToolByName(portal,'portal_properties')

    This issue is related to the vocabulary used for the language field on the 
    default Archetypes types. The vocabulary field does not display combined 
    language codes, even when this option is set on portal_languages.

    The default ExtensibleMetadata language field uses the method 'languages' as 
    vocabulary, this product rename this method to 'languages_old', so we will 
    use it to create a new content and check the returned values.

        >>> id = portal.invokeFactory(type_name='Document',id='foo', title='Foo')
        >>> foo = portal.foo
        >>> languageField = foo.getField('language')
        >>> defaultVocabulary = 'languages_old' # as we already patched the class
        >>> languages = getattr(foo,defaultVocabulary)()

    Then we enable combined language codes on our portal. Also we set pt-br as 
    default language and disable "Start as Neutral":
    
        >>> defaultLanguage = 'pt-br'
        >>> supportedLanguages = ['pt-br', 'en','de','no']
        >>> lt.manage_setLanguageSettings(defaultLanguage,
        ...                              supportedLanguages,
        ...                              setUseCombinedLanguageCodes=True,
        ...                              startNeutral=False)

    After setting portal_languages to allow combined language codes we should get 
    a large number of languages from the vocabulary, but it doesn't happen as we 
    have the same results::

        >>> foo = portal.foo
        >>> languageField = foo.getField('language')
        >>> languagesCombined = getattr(foo,defaultVocabulary)()
        >>> languages == languagesCombined
        True

    So, we now use our vocabulary method and see we will have the complete language 
    list::
    
        >>> foo = portal.foo
        >>> languageField = foo.getField('language')
        >>> newVocabulary = 'languages'
        >>> languagesCombined = getattr(foo,newVocabulary)()
        >>> languages == languagesCombined
        False
        >>> 'pt-br' in languagesCombined
        True

    And if we go back to use only simple language codes ::

        >>> defaultLanguage = 'en'
        >>> supportedLanguages = ['en','de','no']
        >>> lt.manage_setLanguageSettings(defaultLanguage,
        ...                              supportedLanguages,
        ...                              setUseCombinedLanguageCodes=False,
        ...                              startNeutral=False)

    It must work as planned::

        >>> foo = portal.foo
        >>> languageField = foo.getField('language')
        >>> newVocabulary = languageField.vocabulary
        >>> languagesCombined = getattr(foo,newVocabulary)()
        >>> 'pt-br' in languagesCombined
        False

Installing the fix
------------------

    If your using a buildout-based installation all you need to do is declare 
    archetypes.languagebugfix in eggs and zcml sections for you instance.
    
Credits
-------
    
    Development and tests:
        
        * `Simples Consultoria <http://www.simplesconsultoria.com.br/>`_ 
          (products at simplesconsultoria dot com dot br)
    
    Efforts to research and fix this issue were sponsored by:
    
        * `TV1 <http://www.tv1.com.br/>`_
