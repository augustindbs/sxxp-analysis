
import yfinance as yf
import pandas as pd

sxxp = pd.ExcelFile('main/data/sxxp_daily.xlsx')
securities = sxxp.sheet_names


# CONVERT BLOOMBERG TICKERS TO YAHOO FINANCE TICKERS FOR SXXP 600 EQUITIES


acronym_mapping = {
    'NA': '.AS',
    'SW': '.SW',
    'AV': '.VI',
    'FP': '.PA',
    'GR': '.DE',
    'FH': '.HE',
    'IM': '.MI',
    'SM': '.MC',
    'ID': '.IR',
    'PL': '.LS',
    'BB': '.BR',
    'LN': '.L',
    'SS': '.ST',
    'DC': '.CO',
    'NO': '.OL',
    'PW': '.WA'
}

manual_overrides = {
    'ADDTB SS Equity': 'ADDT-B.ST',
    'AIBG ID Equity': 'AIBG.L',
    'AMBUB DC Equity': 'AMBU-B.CO',
    'ASSAB SS Equity': 'ASSA-B.ST',
    'ATCOA SS Equity': 'ATCO-A.ST',
    'BALDB SS Equity': 'BALD-B.ST',
    'BEIJB SS Equity': 'BEIJ-B.ST',
    'CARLB DC Equity': 'CARL-B.CO',
    'COLOB DC Equity': 'COLO-B.CO',
    'EKTAB SS Equity': 'EKTA-B.ST',
    'ELUXB SS Equity': 'ELUX-B.ST',
    'EPIA SS Equity': 'EPI-A.ST',
    'ERICB SS Equity': 'ERIC-B.ST',
    'ESSITYB SS Equity': 'ESSITY-B.ST',
    'GETIB SS Equity': 'GETI-B.ST',
    'GLB ID Equity': 'GLB.L',
    'HEXAB SS Equity': 'HEXA-B.ST',
    'HMB SS Equity': 'HM-B.ST',
    'HOLMB SS Equity': 'HOLM-B.ST',
    'HPOLB SS Equity': 'HPOL-B.ST',
    'HUSQB SS Equity': 'HUSQ-B.ST',
    'INDUC SS Equity': 'INDU-C.ST',
    'INVEB SS Equity': 'INVE-B.ST',
    'KINVB SS Equity': 'KINV-B.ST',
    'KSP ID Equity': 'KRX.IR',
    'KYGA ID Equity': 'KYGA.L',
    'LAGRB SS Equity': 'LAGR-B.ST',
    'LATOB SS Equity': 'LATO-B.ST',
    'LIFCOB SS Equity': 'LIFCO-B.ST',
    'LUNDB SS Equity': 'LUND-B.ST',
    'MAERSKB DC Equity': 'MAERSK-B.CO',
    'NDA FH Equity': 'NDA-FI.HE',
    'NIBEB SS Equity': 'NIBE-B.ST',
    'NOVOB DC Equity': 'NOVO-B.CO',
    'NSISB DC Equity': 'NSIS-B.CO',
    'ROCKB DC Equity': 'ROCK-B.CO',
    'SAABB SS Equity': 'SAAB-B.ST',
    'SAGAB SS Equity': 'SAGA-B.ST',
    'SCAB SS Equity': 'SCA-B.ST',
    'SEBA SS Equity': 'SEB-A.ST',
    'SECTB SS Equity': 'SECT-B.ST',
    'SECUB SS Equity': 'SECU-B.ST',
    'SHBA SS Equity': 'SHB-A.ST',
    'SKAB SS Equity': 'SKA-B.ST',
    'SKFB SS Equity': 'SKF-B.ST',
    'SKG ID Equity': 'SKG.L',
    'SSABB SS Equity': 'SSAB-B.ST',
    'SWECB SS Equity': 'SWEC-B.ST',
    'SWEDA SS Equity': 'SWED-A.ST',
    'TEL2B SS Equity': 'TEL2-B.ST',
    'TIGO SS Equity': 'TIGO-SDB.ST',
    'TRELB SS Equity': 'TREL-B.ST',
    'VOLCARB SS Equity': 'VOLCAR-B.ST',
    'VOLVB SS Equity': 'VOLV-B.ST',
    'WALLB SS Equity': 'WALL-B.ST',
}

sxxp_securities = []

for security in securities:
    if security in manual_overrides:
        sxxp_securities.append(manual_overrides[security])

    else:
        parts = security.split()
        ticker = parts[0]
        acronym = parts[1]
        yahoo_suffix = acronym_mapping.get(acronym, '')
        if yahoo_suffix:
            yahoo_ticker = f"{ticker}{yahoo_suffix}"
            sxxp_securities.append(yahoo_ticker)

