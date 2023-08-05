from dm.ioc import RequiredFeature

dictionary = RequiredFeature('SystemDictionary')

TEMPLATE_DIRS = (
    dictionary['django.templates_dir'],
)

