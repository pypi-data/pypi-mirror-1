from osv import fields, osv

class res_partner_inherited(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'field_demo': fields.text('Text'),
    }

res_partner_inherited()
