from setuptools import setup, find_packages

version = '2.3'

setup(name='ZopeSkel',
      version=version,
      description="A collection of skeletons for quickstarting Zope projects.",
      long_description=open('README.txt').read() + "\n" + 
                       open('HISTORY.txt').read(),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope command-line skeleton project',
      author='Daniel Nouri',
      author_email='daniel.nouri@gmail.com',
      url='',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "PasteScript",
        "Cheetah",
      ],
      tests_require=['zope.testing', 'zc.buildout', 'Cheetah', 'PasteScript'],
      test_suite='zopeskel.tests.test_zopeskeldocs.test_suite',
      entry_points="""
      [paste.paster_create_template]
      basic_namespace = zopeskel:BasicNamespace
      nested_namespace = zopeskel:NestedNamespace
      basic_zope = zopeskel:BasicZope
      plone = zopeskel:Plone
      plone_app = zopeskel:PloneApp
      plone2_theme = zopeskel:Plone2Theme
      plone2.5_theme = zopeskel:Plone25Theme
      plone3_theme = zopeskel:Plone3Theme
      plone2.5_buildout = zopeskel:Plone25Buildout
      plone3_buildout = zopeskel:Plone3Buildout
      archetype = zopeskel:Archetype
      plone3_portlet = zopeskel:Plone3Portlet
      plone_hosting = zopeskel.hosting:StandardHosting
      recipe = zopeskel:Recipe
      silva_buildout = zopeskel:SilvaBuildout
      plone_pas = zopeskel:PlonePas

      [paste.paster_command]
      addcontent = zopeskel.localcommands:ZopeSkelLocalCommand
      
      [zopeskel.zopeskel_sub_template]
      portlet = zopeskel.localcommands.archetype:Portlet
      view = zopeskel.localcommands.archetype:View
      zcmlmeta = zopeskel.localcommands.archetype:ZCMLMetaDirective
      contenttype = zopeskel.localcommands.archetype:ContentType
      atschema = zopeskel.localcommands.archetype:ATSchemaField

      extraction_plugin = zopeskel.localcommands.plone_pas:ExtractionPlugin
      authentication_plugin = zopeskel.localcommands.plone_pas:AuthenticationPlugin
      challenge_plugin = zopeskel.localcommands.plone_pas:ChallengePlugin
      credentials_reset_plugin = zopeskel.localcommands.plone_pas:CredentialsResetPlugin
      user_adder_plugin = zopeskel.localcommands.plone_pas:UserAdderPlugin
      role_assigner_plugin = zopeskel.localcommands.plone_pas:RoleAssignerPlugin
      user_factory_plugin = zopeskel.localcommands.plone_pas:UserFactoryPlugin
      anonymous_user_factory_plugin = zopeskel.localcommands.plone_pas:AnonymousUserFactoryPlugin
      properties_plugin = zopeskel.localcommands.plone_pas:PropertiesPlugin
      groups_plugin = zopeskel.localcommands.plone_pas:GroupsPlugin
      roles_plugin = zopeskel.localcommands.plone_pas:RolesPlugin
      update_plugin = zopeskel.localcommands.plone_pas:UpdatePlugin
      validation_plugin = zopeskel.localcommands.plone_pas:ValidationPlugin
      user_enumeration_plugin = zopeskel.localcommands.plone_pas:UserEnumerationPlugin
      group_enumeration_plugin = zopeskel.localcommands.plone_pas:GroupEnumerationPlugin
      role_enumeration_plugin = zopeskel.localcommands.plone_pas:RoleEnumerationPlugin
      """,
      )
