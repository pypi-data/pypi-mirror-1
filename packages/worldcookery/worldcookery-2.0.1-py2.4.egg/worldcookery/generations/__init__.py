from zope.app.generations.generations import SchemaManager

WorldCookerySchemaManager = SchemaManager(
    minimum_generation=0,
    generation=2,
    package_name='worldcookery.generations'
    )