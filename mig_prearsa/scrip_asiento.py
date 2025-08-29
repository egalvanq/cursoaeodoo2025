import pandas as pd
from odoo_rpc_client import Client

def execute(model, method, *args, **kwargs):
    return client.execute(model, method, *args, **kwargs)

# ==================== CONFIGURACIÓN ====================
CODIGO_DIARIO_APERTURA = "MIGRA"
FECHA_ASIENTO = "2025-01-01"
NOMBRE_ASIENTO = "Asiento de apertura 2025"

EXCEL_PATH = "contabilidad_filtrada_LANTIGUA.xlsx"
# =======================================================

client = Client(
    "10.0.5.86",
    dbname="prefabricados_134_2025-01-13",
    user="admin",
    pwd="prearsa_2021@",
    port=8069,
    protocol="json-rpc",
)


# === Leer y preparar datos desde Excel ===
df = pd.read_excel(EXCEL_PATH)
df.columns = ['Cuenta', 'DENOMINACION','SALDO']
df = df[df['Cuenta'].notna()]
df['Cuenta'] = df['Cuenta'].astype(str).str.replace('.', '', regex=False)
max_length = df['Cuenta'].str.len().max()
df = df[df['Cuenta'].str.len() == max_length]

ACCOUNT_CODE_PARTNER =['410','430','400','401','411','438','436','446','43100']
lines = []
for _, row in df.iterrows():
    saldo = row['SALDO']
    if saldo <0 or saldo >0:
        vals={
            'name': row['DENOMINACION'],
            'account_code': row['Cuenta'].strip(),
            'debit': round(saldo, 2) if saldo > 0 else 0.0,
            'credit': round(-saldo, 2) if saldo < 0 else 0.0,
        }
        print(vals)
        lines.append(vals)
    
chang_account_ids = client["account.account"].search_records([])
print(chang_account_ids)
for acc in chang_account_ids:
    if len(acc.code) == 6:
        new_code = acc.code.ljust(10,"0")
        acc.write({'code': new_code})
        

# Obtener ID del diario
journal_ids = client["account.journal"].search([("code", "=", CODIGO_DIARIO_APERTURA)])
if not journal_ids:
    raise ValueError(f"No se encontró diario con código '{CODIGO_DIARIO_APERTURA}'")
journal_id = journal_ids[0]

# Buscar cuentas y construir líneas
move_lines = []
for line in lines:
    account_code = line['account_code'].strip()
    account_ids = client["account.account"].search_read([("code", "=", account_code),("company_id", "=", 2)], limit=1)
    partner_id = False
    if not account_ids:
        print(f"⚠️  Cuenta no encontrada en Odoo: {account_code}")
        prefix = account_code[:3]
        if prefix not in ACCOUNT_CODE_PARTNER:
            base_id = client["account.account"].search_records([("code", "like", prefix + "%")],limit=1)
            if base_id:
                # print(f"    - Se usará la cuenta base: {base_id[0]['code']} - {base_id[0].user_type_id.id} - {base_id[0].group_id.id}")
                account_type = base_id[0].user_type_id.id
                group_id = base_id[0].group_id.id
            else:
                account_type = "off_balance"
                group_id = False
            vals={
                "code": account_code,
                "name": line["name"].strip(),
                "user_type_id": account_type,
                "group_id": group_id,
            }
            
            new_id = client["account.account"].create(vals)
            account_ids = client["account.account"].search_records([("id", "=", new_id )],limit=1)

    if account_code[:3] in ACCOUNT_CODE_PARTNER:
        code_account = account_code
        partners = client["res.partner"].search_records([("comment", "like", "%"+code_account+"%")],limit=1)
        if partners:
            partner_id = partners[0]["id"]
    if not account_ids:
        prefix = account_code[:3].ljust(10,"0")
        account_ids = client["account.account"].search_records([("code", "=", prefix)],limit=1)

    vals_journal = {
        'name': line['name'].strip(),
        'account_id': account_ids[0]["id"],
        'partner_id': partner_id or False,
        'debit': line['debit'],
        'credit': line['credit'],
    }
    move_lines.append((0, 0, vals_journal))

# Crear el asiento contable
move_id = client["account.move"].create({
    'ref': NOMBRE_ASIENTO,
    'date': FECHA_ASIENTO,
    'journal_id': journal_id,
    'line_ids': move_lines,
    # 'move_type': 'entry',
})
print(f"✅ Asiento de apertura creado con ID: {move_id}")