from zope.app.generations.generations import SchemaManager

schemaManager = SchemaManager(
    minimum_generation=1,
    generation=1,
    package_name='zcontact.generations')
