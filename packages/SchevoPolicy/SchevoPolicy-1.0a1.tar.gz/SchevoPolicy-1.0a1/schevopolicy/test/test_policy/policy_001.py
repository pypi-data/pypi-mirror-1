from schevopolicy.schema import *
schevopolicy.schema.prep(locals())


default = ALLOW


@allow_t.when(
    "extent is db.Foo and "
    "t_name == 'create'"
    )
def allow_t(db, context, extent, entity, t_name):
    return True
