import pandas as pd
import odoorpc 
import re

archivo_excel = "contabilidad_filtrada_LANTIGUA.xlsx"
archivo = pd.read_excel(archivo_excel)

odoo = odoorpc.ODOO('10.0.5.86', port=8069)
odoo.login('prefabricados_134_2025-01-13', 'admin', 'prearsa_2021@')

archivo.sort_values(by="Cuenta", inplace=True)
cont_encontradas=0
cont_creadas=0
array_encontradas = []
array_creadas = []
count_if400=0
for index, fila in archivo.iterrows():
    # print(f"Procesando fila {index + 1} de {len(archivo)}")
    account_obj = odoo.env['account.account'].search([('code','=',str(fila["Cuenta"])),('company_id','=',2)],limit=1)
    if account_obj:
        print(f"Cuenta encontrada: {fila["Cuenta"]} - {odoo.env['account.account'].browse(account_obj[0]).name}")

        # with open("log.txt",'a', encoding='utf-8')as log:
        #     log.write(f"{fila["Cuenta"]},\n")
        cont_encontradas += 1
        array_encontradas.append(fila["Cuenta"])
    
    else:
        if str(fila["Cuenta"])[:3] not in ['410','430','400','401','411','438','436','446'] and str(fila["Cuenta"])[:5] not in['43100']:
            # print(f"Cuenta NO encontrada: {fila["Cuenta"]} - {fila["DENOMINACION"]}")
            user_type_id = None
            num_cuenta = len(str(fila["Cuenta"]))
            for i in [4,3,2,1]:
                num = num_cuenta - i
                codigo = str(fila["Cuenta"])
                code = codigo[:i]+num*'0'
                # print(code)
                account_obj = odoo.env['account.account'].search([('code','=',code)],limit=1)
                if account_obj:
                    user_type_id = odoo.env['account.account'].browse(account_obj[0]).user_type_id
                    # print(f"Tipo de cuenta sugerido (por prefijo : {str(fila['Cuenta'])[:i]}): {user_type_id.name}, ID: {user_type_id.id}")
                    break

            group_id = None
            for i in [4,3,2,1]:
                group_ids = odoo.env['account.group'].search([('code_prefix','=',str(fila["Cuenta"])[:i])],limit=1)
                if group_ids:
                    group_id = group_ids[0]
                    # print(f"group_ids[0] de cuenta sugerido (por prefijo : {str(fila['Cuenta'])[:i]}): {odoo.env['account.group'].browse(group_id).name}, ID: {group_id}")
                    break
            if not group_id:
                for i in [4,3,2,1]:
                    num_group = num_cuenta - i
                    codigo_group = str(fila["Cuenta"])
                    code_group = codigo_group[:i]+num_group*'0'
                    group_id_aux = odoo.env['account.account'].search([('code','=',code_group)])
                    if group_id_aux:
                        group_obj = odoo.env['account.account'].browse(group_id_aux[0]).group_id
                        if group_obj:
                            group_id = group_obj.id
                            # print(f"group_obj de cuenta sugerido (por prefijo : {str(fila['Cuenta'])[:i]}): {group_obj.name}, ID: {group_id}")
                            break
            concilia = False
            if user_type_id.name in ["Por cobrar","A pagar"]:
                concilia = True
            # print(f"Tipo de cuenta: {user_type_id.name if user_type_id else 'No encontrado'}")
            # print(f"Conciliación: {concilia}")
            partner_ids = odoo.env['res.partner'].search([('comment','ilike',str(fila["Cuenta"]))])
            # print(odoo.env['res.partner'].browse(partner_ids).name)
            parner_name = odoo.env['res.partner'].browse(partner_ids).name
            
            
            if user_type_id and group_id:
                new_account = {
                    'code': str(fila["Cuenta"]),
                    'name': fila["DENOMINACION"],
                    'user_type_id': user_type_id.id,
                    'group_id': group_id,
                    'reconcile': concilia,
                    'company_id': 2,
                }
            if str(fila["Cuenta"]) == '1290000001':
                new_account = {
                    'code': str(fila["Cuenta"]),
                    'name': fila["DENOMINACION"],
                    'user_type_id': 10,
                    'group_id': 33,
                    'reconcile': False,
                    'company_id': 2,
                }
            # print(new_account)
            created_account_id = odoo.env['account.account'].create(new_account)
            cuenta_creada = odoo.env['account.account'].browse(created_account_id)
            cont_creadas += 1
            array_creadas.append(cuenta_creada.code)
            print(f"Cuenta creada: {cuenta_creada.code} - {cuenta_creada.name}")
        else:
            count_if400 += 1
                
with open("log.txt",'a', encoding='utf-8')as log:
    log.write(f"cuentas encontradas:{cont_encontradas} - {array_encontradas} -{len(array_encontradas)}\ncuentas creadas:{cont_creadas}-{array_creadas}--{len(array_creadas)}\n 400:{count_if400}")
            
