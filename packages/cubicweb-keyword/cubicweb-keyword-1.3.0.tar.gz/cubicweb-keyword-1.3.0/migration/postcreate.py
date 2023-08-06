# postcreate script. You could setup a workflow here for example
# no explicit initial state for Keywords since it depends on the user's groups
pending = add_state(_('validation pending'), 'Keyword')
validated = add_state(_('keyword validated'), 'Keyword')
rejected = add_state(_('keyword rejected'), 'Keyword')
add_transition(_('validate keyword'), 'Keyword', (pending,), validated,
               requiredgroups=('managers',))
add_transition(_('reject keyword'), 'Keyword', (pending,), rejected,
               requiredgroups=('managers',))

