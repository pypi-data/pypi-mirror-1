Supported options
=================

The recipe supports the following options:

.. Note to recipe author!
   ----------------------
   For each option the recipe uses you shoud include a description
   about the purpose of the option, the format and semantics of the
   values it accepts, whether it is mandatory or optional and what the
   default value is if it is omitted.

zope2location

    A path to a Zope2 instance

name

    The name of the mail queue delivery utility. Default to iw.mailer.

host

    Your smtp host. Default to localhost.

port

    Yout smtp port. Default to 25.

username

    Login name if required by smtp server.

password

    Password if required by smtp server

mailqueue

    A path to an existing directory to create a mailqueue. Default to var/.
    Be aware that this need to be an *absolute* path.


Example usage
=============

   The PyPI page for zc.buildout contains documentation about the test
   environment.

     http://pypi.python.org/pypi/zc.buildout#testing-support

   Below is a skeleton doctest that you can start with when building
   your own tests.

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = mailer
    ...
    ... [mailer]
    ... recipe = iw.recipe.sendmail
    ... zope2location=parts/zope2
    ... host = smtp.example.com
    ... """)

Simulate the Zope2 part::

    >>> mkdir('parts','zope2')
    >>> mkdir('parts','zope2','etc')

Running the buildout gives us::

    >>> print system(buildout)
    Installing mailer.
    iw.sendmail-configure.zcml: Generated file 'iw.sendmail-configure.zcml'.

And see the results zcml stub::

    >>> cat('parts','zope2','etc','package-includes',
    ...                           'iw.sendmail-configure.zcml')
    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:zcml="http://namespaces.zope.org/zcml">
    <BLANKLINE>
        <include package="zope.sendmail" file="meta.zcml" />
    <BLANKLINE>
        <configure
            xmlns:mail="http://namespaces.zope.org/mail">
    <BLANKLINE>
            <mail:smtpMailer
                name="iw.smtp"
                hostname="smtp.example.com"
                port="25"
                />
    <BLANKLINE>
            <mail:queuedDelivery
                name="iw.mailer"
                permission="zope.Public"
                mailer="iw.smtp"
                queuePath="/sample-buildout/var/mailqueue"
                />
        </configure>
    <BLANKLINE>
        <configure zcml:condition="installed iw.mailhost">
            <include package="iw.mailhost" />
        </configure>
    <BLANKLINE>
    </configure>

Let's try with all parameters::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = mailer
    ...
    ... [mailer]
    ... recipe = iw.recipe.sendmail
    ... zope2location=parts/zope2
    ... name = mailer
    ... host = smtp.example2.com
    ... port = 50
    ... username = gael
    ... password = xxx
    ... mailqueue = ${buildout:directory}
    ... """)

Running the buildout again::

    >>> print system(buildout)
    Uninstalling mailer.
    Installing mailer.
    iw.sendmail-configure.zcml: Generated file 'iw.sendmail-configure.zcml'.

And see the results zcml stub::

    >>> cat('parts','zope2','etc','package-includes',
    ...                           'iw.sendmail-configure.zcml')
    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:zcml="http://namespaces.zope.org/zcml">
    <BLANKLINE>
        <include package="zope.sendmail" file="meta.zcml" />
    <BLANKLINE>
        <configure
            xmlns:mail="http://namespaces.zope.org/mail">
    <BLANKLINE>
            <mail:smtpMailer
                name="iw.smtp"
                hostname="smtp.example2.com"
                port="50"
                username="gael"
                password="xxx"
                />
    <BLANKLINE>
            <mail:queuedDelivery
                name="mailer"
                permission="zope.Public"
                mailer="iw.smtp"
                queuePath="/sample-buildout/mailqueue"
                />
        </configure>
    <BLANKLINE>
        <configure zcml:condition="installed iw.mailhost">
            <include package="iw.mailhost" />
        </configure>
    <BLANKLINE>
    </configure>

