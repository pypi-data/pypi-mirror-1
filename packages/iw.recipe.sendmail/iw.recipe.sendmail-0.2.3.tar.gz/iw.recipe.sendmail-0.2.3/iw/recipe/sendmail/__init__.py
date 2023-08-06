# -*- coding: utf-8 -*-
"""Recipe sendmail"""

import os
from zc.buildout import UserError
from iw.recipe.template import Template

class Recipe(Template):
    """zc.buildout recipe"""
    template_dir = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.name = 'iw.sendmail-configure.zcml'
        self.source = os.path.join(self.template_dir, 'template.zcml_tmpl')
        zope2location = options.get('zope2location')
        if not zope2location:
            raise UserError('zope2location is required for iw.recipe.mailer')

        # The 'package-includes' directory is created only if there is one zcml
        # file declared in the zope standalone or in all zeo clients.
        includes_path = os.path.join(options.get('zope2location'),
                                     'etc', 'package-includes')
        if not os.path.exists(includes_path):
            os.makedirs(includes_path)

        self.destination = includes_path

        options.setdefault('name', 'iw.mailer')
        options.setdefault('host', 'localhost')
        options.setdefault('port', '25')
        mailqueue = options.get('mailqueue', None)
        if mailqueue is not None:
            options['mailqueue'] = os.path.join(mailqueue, 'mailqueue')
        else:
            options.setdefault('mailqueue', os.path.join(
                    buildout['buildout']['directory'],'var', 'mailqueue'))

        self.kwargs = dict(name=name,
                           options=options,
                           buildout=buildout)

