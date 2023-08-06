Introduction
============

Since Plone 4, the list of fields which are available as "user data" are stored
in a schema called IUserDataSchema. The new package plone.app.users_ is
responsible for this. It allows the site administrator to define which fields
should appear on the registration form.

This product shows you how you could extend or modify this schema, so you can
create a product which customizes the available fields on the registration
form.


How it works
============

More information in detail about how you change the fields which appear on the
registration form.

Overriding the default schema 
-----------------------------

The default IUserDataSchema is defined in plone.app.users. To override it, we
add a file ``configure.zcml``, which overrides plone.app.users'
UserDataSchemaProvider with the one from our example product.

Adding the "Country" field
--------------------------

We registered our own UserDataSchemaProvider, which lives in
``userdataschema.py``. We create a new schema class here:

::

    class IEnhancedUserDataSchema(IUserDataSchema):
        """ Use all the fields from the default user data schema, and add:
        - country
        """
        country = schema.TextLine(
            title=_(u'label_country', default=u'Country'),
            description=_(u'help_country',
                          default=u"Fill in which country you live in."),
            required=False,
            )    

Adding various other fields
---------------------------

There are various other extra fields with which you could extend your users'
profile. In ``userdataschema.py`` you will find examples for:

    - a Date field (``birthdate``)
    - a Bool field (``newsletter``)
    - a Bool field which is required for signup (``accept``)
    - a Choice field (``gender``)

.. _plone.app.users: http://pypi.python.org/pypi/plone.app.users


