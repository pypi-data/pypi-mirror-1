"""
Elixir statements supporting entity lifecycle callback functions.
"""

from elixir.statements import Statement
from sqlalchemy.orm.mapper import MapperExtension
import types

def proxy_to_instance(name):
    def new_func(self, mapper, connection, instance):
        if hasattr(instance, name) : getattr(instance, name)()  
    return new_func

def mapper_extension_statement(name):
    def init(self, entity, *callbacks):
        def proxy_method(self):
            for callback in callbacks:
                getattr(self, callback)()
        setattr(entity, '__%s__' %name, proxy_method)
        extensions = entity._descriptor.mapper_options.get('extension', [])
        if type(extensions) is not types.ListType: 
            extensions = [extensions]
        if ext_proxy not in extensions:
            extensions.append(ext_proxy)
            entity._descriptor.mapper_options['extension'] = extensions
    return type('MapperExtensionStatement', (object, ), {'__init__':init})

class MapperExtensionProxy(MapperExtension):
        
    after_delete = proxy_to_instance('__after_delete__')
    after_insert = proxy_to_instance('__after_insert__')
    after_update = proxy_to_instance('__after_update__')
    before_delete = proxy_to_instance('__before_delete__')
    before_insert = proxy_to_instance('__before_insert__')
    before_update = proxy_to_instance('__before_update__')
            
ext_proxy = MapperExtensionProxy()

after_delete = Statement(mapper_extension_statement('after_delete'))            
after_insert = Statement(mapper_extension_statement('after_insert'))            
after_update = Statement(mapper_extension_statement('after_update'))            
before_delete = Statement(mapper_extension_statement('before_delete'))          
before_insert = Statement(mapper_extension_statement('before_insert'))          
before_update = Statement(mapper_extension_statement('before_update'))