import pandas as pd
import odoorpc 

odoo = odoorpc.ODOO('10.0.5.86', port=8069)
odoo.login('prefabricados_134_2025-01-13', 'admin', 'prearsa_2021@')

archivo_excel = "contactos_lantigua.xlsx"
archivo = pd.read_excel(archivo_excel)

archivo.sort_values(by="CUENTA", inplace=True)

for index, fila in archivo.iterrows():
    fila_dict = fila.to_dict()
    #print(fila_dict)
    vat = fila_dict.get("C.I.F.")
    if pd.isna(vat):
        print("VAT is missing")
    else:
        #=== Buscar partner por VAT ===
        vat_busqueda = "ES" + str(vat)
        partner = odoo.env['res.partner'].search([('vat', '=', vat_busqueda)])
        if partner:
            #=== Actualizar datos del partner existente, añadir cuenta formateada al partner en notas internas ===
            cuenta = str(fila_dict.get("CUENTA"))
           
            partner_obj = odoo.env['res.partner'].browse(partner[0])

            comment_cuenta = partner_obj.comment or ""
           
            if cuenta and cuenta.startswith('239'):
                comment_cuenta += '\n'
                comment_cuenta += f'[239][{cuenta}]'
               
            if cuenta and (cuenta.startswith('400') or cuenta.startswith('410')):
                comment_cuenta += '\n'
                comment_cuenta += f'[LA][PAY][{cuenta}]'
           
            if cuenta and cuenta.startswith('430'):
                comment_cuenta += '\n'
                comment_cuenta += f'[REC][{cuenta}]'
           
            if cuenta and cuenta.startswith('523'):
                comment_cuenta += '\n'
                comment_cuenta += f'[LA][ACTV][{cuenta}]'

            if fila_dict.get("CONTACTO") and pd.notna(fila_dict.get("CONTACTO")):
                contacto = fila_dict.get("CONTACTO")
                contacto_hijo = odoo.env['res.partner'].search([('name', '=', contacto), ('parent_id', '=', partner[0])])
                if not contacto_hijo:
                    odoo.env['res.partner'].create({
                        'name': contacto,
                        'parent_id': partner[0],                    
                    })

            if partner_obj.phone is False and pd.notna(fila_dict.get("Teléfono-1")):
                partner_obj.write({'phone': fila_dict.get("Teléfono-1")})

            if partner_obj.fax is False and pd.notna(fila_dict.get("FAX")):   
                partner_obj.write({'fax': fila_dict.get("FAX")})

            partner_obj.write({'comment': comment_cuenta})

        else:
            
            #=== Crear nuevo partner ===
            cuenta = str(fila_dict.get("CUENTA"))
           
            comment_cuenta = ""  
           
            if cuenta and cuenta.startswith('239'):
                comment_cuenta = f'[239][{cuenta}]'
               
            if cuenta and (cuenta.startswith('400') or cuenta.startswith('410')):  
                comment_cuenta = f'[LA][PAY][{cuenta}]'
           
            if cuenta and cuenta.startswith('430'):
                comment_cuenta = f'[REC][{cuenta}]'
           
            if cuenta and cuenta.startswith('523'):
                comment_cuenta = f'[LA][ACTV][{cuenta}]'


            parent_id = odoo.env['res.partner'].create({
                
                'name': fila_dict.get("Razón Social o nombre"),
                'vat': vat_busqueda,
                'phone': fila_dict.get("Teléfono-1") if pd.notna(fila_dict.get("Teléfono-1")) else False,
                'fax': fila_dict.get("FAX") if pd.notna(fila_dict.get("FAX")) else False,
                'street': fila_dict.get("Calle") if pd.notna(fila_dict.get("Calle")) else False,
                'zip': str(int(fila_dict.get("Código postal"))).zfill(5) if pd.notna(fila_dict.get("Código postal")) else False,
                'country_id': odoo.env['res.country'].search([('name', '=', 'España')], limit=1)[0] if odoo.env['res.country'].search([('name', '=', 'España')], limit=1) else False,
                'state_id': odoo.env['res.country.state'].search([('name', 'ilike', fila_dict.get("Provincia"))], limit=1)[0] if fila_dict.get("Provincia") and pd.notna(fila_dict.get("Provincia")) and odoo.env['res.country.state'].search([('name', 'ilike', fila_dict.get("Provincia"))], limit=1) else False,
                'city': fila_dict.get("Ciudad") if pd.notna(fila_dict.get("Ciudad")) else False,
                'comment': comment_cuenta
            })
            if fila_dict.get("CONTACTO") and pd.notna(fila_dict.get("CONTACTO")):
                contacto = fila_dict.get("CONTACTO")
                odoo.env['res.partner'].create({
                    'name': contacto,
                    'parent_id': parent_id,
                })
                



