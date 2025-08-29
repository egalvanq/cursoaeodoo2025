import odoorpc

odoo = odoorpc.ODOO('10.0.5.86', port=8069)
odoo.login('prefabricados_134_2025-01-13', 'admin', 'prearsa_2021@')

partner_ids = odoo.env['res.partner'].search([('create_date', '>', '2025-08-25 00:00:00')])
for partner_id in partner_ids:
    partner = odoo.env['res.partner'].browse(partner_id)
    partner.unlink()