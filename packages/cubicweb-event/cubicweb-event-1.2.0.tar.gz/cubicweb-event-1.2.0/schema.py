from cubicweb.schema import format_constraint

class Event(EntityType):
    """a calendar event"""
    title = String(required=True, fulltextindexed=True, maxsize=128)
    diem = Datetime(required=True)
    end_date = Datetime(required=False)
    type = String(internationalizable=True,
                  vocabulary=(_('appointment'), _('convention'), _('meeting'),
                              _('social event'), _('work'), _('training')),
                  default='appointment')
    location    = String(fulltextindexed=True, maxsize=256)
    description_format = String(meta=True, internationalizable=True, maxsize=50,
                                default='text/rest', constraints=[format_constraint])
    description = String(fulltextindexed=True)
    
