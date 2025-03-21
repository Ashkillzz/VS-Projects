import xml.etree.ElementTree as ET
import json
import re

def extract_fields(xml_file, field_map):

    tree = ET.parse(xml_file)       
    root = tree.getroot()       ## Obtains root element of tree in root obj
    extracted_data = {}     ## Empty Dict to store key-value pairs based on custom mapping dict
    
    for xml_tag, json_key in field_map.items():        
        for element in root.iter(xml_tag):      ## Iterates through the entire XML tree
            text = element.text.replace('\n' , ' ').strip() if element.text else None       
            if json_key not in extracted_data:      
                if text == None:
                    extracted_data[json_key] = text
                elif ('.' in  text) and (re.fullmatch(r"-?\d+(\.\d+)?",text)):
                    extracted_data[json_key] = "{:.2f}".format(float(text))
                elif xml_tag == 'PHONE_NUMBER':
                    extracted_data[json_key] = text
                else:
                    try: 
                        int(text)
                        extracted_data[json_key] = str(int(text))

                    except ValueError:
                        extracted_data[json_key] = text
                
                break

    return extracted_data

def extract_content_fromto(xml_file, fields, start, end):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    extracted_data2 = {}
    in_range = False

    for xml_tag, json_key in fields.items():
        for elem in root.iter(xml_tag):
            
            if json_key in extracted_data2 and extracted_data2[json_key] != None:
                break

            elif elem.tag == start:
                extracted_data2[json_key] = str(float(elem.text)) if elem.text else None
                in_range = True
                

            elif elem.tag == end:
                extracted_data2[json_key] = "{:.2f}".format(float(elem.text)) if elem.text else None

            elif in_range and elem.tag not in (start, end):
                if elem.text is not None:
                    if ('.' in elem.text) and re.fullmatch(r"-?\d+(\.\d+)?", elem.text): 
                        extracted_data2[json_key] = "{:.2f}".format(float(elem.text)) 
                    else:
                        try:
                            extracted_data2[json_key] = str(int(elem.text)) 
                        except ValueError:
                            extracted_data2[json_key] = elem.text 
                else:
                    extracted_data2[json_key] = elem.text


    return extracted_data2

def extract_tables2(xml_file, fields, title):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    records = {}

    for record in root.iter(title):
        for xml_tag, json_key in fields.items():
            for elem in record:
                if xml_tag == elem.tag and json_key not in records.keys():
                    if ('.' in  elem.text) and (re.fullmatch(r"-?\d+(\.\d+)?",elem.text)):
                        extracted_data[json_key] = "{:.2f}".format(float(elem.text))
                    else:
                        try: 
                            int(elem.text)
                            extracted_data[json_key] = str(int(elem.text))

                        except ValueError:
                            extracted_data[json_key] = elem.text
                    break


    return records

def extract_tables(xml_file, fields, header):   ## To extract from tables with dynamic size
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    records = []
    n = len(fields)

    for record in root.iter(header):
        for sub in record:
            count = 0
            sub_records = {}
            for xml_tag, json_key in fields.items():
                for child in sub:
                    if child.tag == xml_tag:
                        if child.text != None:
                            if ('.' in  child.text) and (re.fullmatch(r"-?\d+(\.\d+)?",child.text)):
                                child.text = "{:.2f}".format(float(child.text))
                                sub_records[json_key] = str(child.text)
                            else:
                                try: 
                                    int(child.text)
                                    sub_records[json_key] = str(int(child.text))

                                except ValueError:
                                    sub_records[json_key] = str(child.text)
                        else:
                            sub_records[json_key] = None
                            count+=1 
                        break
            if count < n:
                records.append(sub_records)
    
    return records

def save_to_json(data, json_file, name):

    try:
        # Read existing content from the file
        with open(json_file, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file does not exist or is empty/invalid, initialize as an empty dictionary
        existing_data = {}

    if name == "Equity_Share_Fixed":
        temp_dict = {'Equity_Shares_Fixed' : data}
        existing_data["Share_Capital"] = temp_dict

    elif name == "Pref_Share_Fixed":
        temp_dict = {'Preference_Shares_Fixed' : data}
        existing_data["Share_Capital"].update(temp_dict)

    elif name == "Equity_Shares_Dynamic":
        temp_dict = {'Equity_Shares_Dynamic' : data}
        existing_data["Share_Capital"].update(temp_dict)

    elif name == "Pref_Shares_Dynamic":
        temp_dict = {'Preference_Shares_Dynamic' : data}
        existing_data["Share_Capital"].update(temp_dict)

    elif name == "Rem_Num_MgDt":
        temp_dict = {'Managing_Dt' : data}
        existing_data["Remuneration"] = temp_dict

    elif name == "Rem_Num_MgDt":
        temp_dict = {'Other_Dt' : data}
        existing_data["Remuneration"].update(temp_dict)

    elif name not in existing_data:
        existing_data[name] = data

    # Write the updated data back to the file
    with open(json_file, 'w') as file:
        json.dump(existing_data, file, indent=4)

if __name__ == "__main__":

    xml_file_path = 'D:\Aswin\VS Projects\Form MGT-7A-25112024_data.xml'

    json_path = "MGT7A.json"

    Regular = {
        'CIN' : 'cin',
        'GLN' : 'gln',
        'IT_PAN_OF_COMPNY' : 'pan',
        'NAME_OF_COMPANY' : 'nmc',
        'REG_OFFC_ADDRESS' : 'roa',
        'EMAIL_ID_COMPANY' : 'eidc',
        'PHONE_NUMBER' : 'tnstd',
        'WEBSITE' : 'wb',
        'INCORPORATION_DATE' : 'dtinc',
        'TYPE_OF_COMPANY' : 'toc',
        'CATEGORY_COMPANY' : 'cgoc',
        'SUB_CATEGORY_COM' : 'scgoc',
        'RB_SHARE_CAPITAL' : 'csc',
        'RB_OPC_SC' : 'frmfd',
        'RB_SHARE_LISTED' : 'slrse',
        'FY_FROM_DATE' : 'fyfm',
        'FY_END_DATE' : 'fyto',
        'RB_AGM_HELD' : 'isagm',
        'DATE_AGM' : 'dtagm',
        'DUE_DATE_AGM' : 'dueagm',
        'RB_AGM_EXTENSION' : 'extgtd',
        'SRN_FORM_EXTNSN' : 'srnext',
        'DUE_DATE_AGM_2' : 'extdd',
        'REASONS' : 'rsn',
        'NO_BUSINESS_ACT' : 'nba',
        'NO_OF_CLASSES_ES' : 'nces',
        'NO_OF_CLASSES_PS' : 'ncps',
        'TOT_AMT_UC_SHARE' : 'tucsh',
        'TOT_TURNOVER' : 'to',
        'NET_WORTH_COMP' : 'nwc',
        'TOT_NO_SHARE_HLD' : 'tsp',
        'TOT_NO_SHR_HLD_P' : 'tsop',
        'TOT_NO_SH_PR_PUB' : 'tsppo',
        'RB_COMP_COMPLAIN' : 'cpdsc',
        'IF_NO_REASONS' : 'ifno',
        'CVRN' : 'bdvrn',
        'DATE_DECLARATION' : 'bdcdt',
        'DIN_OF_DIRECTOR' : 'dindr'
    }

    Bus_act = {
        'MAIN_ACT_GRP_COD'  : 'magc',
        'DES_MAIN_ACT_GRP' : 'dmag',
        'BUSINESS_ACT_COD' : 'bac',
        'DES_BUSINESS_ACT' : 'dba',
        'PERCENT_TURN_OVR' : 'ptc'   
    }

    Part_Asc_Comp = {
        'NAME_COMPANY' : 'noc',
        'CIN_FCRN' : 'cin',
        'HOLD_SUB_ASSOC' : 'ascjv',
        'PERCENT_SHARE' : 'psh'
    }

    Equ_shr_fixed = {
        'TOT_NO_ES_A_CAP' : 'tneac',
        'TOT_NO_ES_I_CAP' : 'tneic',
        'TOT_NO_ES_S_CAP' : 'tnesc',
        'TOT_NO_ES_P_CAP' : 'tnepc',
        'TOT_AMT_ES_A_CAP' : 'taeac',
        'TOT_AMT_ES_I_CAP' : 'taeic',
        'TOT_AMT_ES_S_CAP' : 'taesc',
        'TOT_AMT_ES_P_CAP' : 'taepc'
    }

    Pref_shr_fixed = {
        'TOT_NO_PS_A_CAP' : 'tnpac',
        'TOT_NO_PS_I_CAP' : 'tnpic',
        'TOT_NO_PS_S_CAP' : 'tnpsc',
        'TOT_NO_PS_P_CAP' : 'tnppc',
        'TOT_AMT_PS_A_CAP' : 'tapac',
        'TOT_AMT_PS_I_CAP' : 'tapic',
        'TOT_AMT_PS_S_CAP' : 'tapsc',
        'TOT_AMT_PS_P_CAP' : 'tappc'
    }

    Equ_shr = {
        'NO_ES_A_CAP' : 'nesac',
        'NO_ES_I_CAP' : 'nesic',
        'NO_ES_S_CAP' : 'nessc',
        'NO_ES_P_CAP' : 'nespc',
        'NOM_VAL_ES_A_CAP' : 'nvac',
        'NOM_VAL_ES_I_CAP' : 'nvic',
        'NOM_VAL_ES_S_CAP'  : 'nvsc',
        'NOM_VAL_ES_P_CAP' : 'nvpc',
        'TOT_AMT_ES_A_CAP' : 'taesac',
        'TOT_AMT_ES_I_CAP' : 'taesic',
        'TOT_AMT_ES_S_CAP' : 'taessc',
        'TOT_AMT_ES_P_CAP' : 'taespc'
    }

    Pref_shr = {
        'NO_PS_A_CAP' : 'npsac',
        'NO_PS_I_CAP' : 'npsic',
        'NO_PS_S_CAP' : 'npssc',
        'NO_PS_P_CAP' : 'npspc',
        'NOM_VAL_PS_A_CAP' : 'nvac',
        'NOM_VAL_PS_I_CAP' : 'nvic',
        'NOM_VAL_PS_S_CAP' : 'nvsc',
        'NOM_VAL_PS_P_CAP' : 'nvpc',
        'TOT_AMT_PS_A_CAP' : 'tapsac',
        'TOT_AMT_PS_I_CAP' : 'tapsic',
        'TOT_AMT_PS_S_CAP' : 'tapssc',
        'TOT_AMT_PS_P_CAP' : 'tapspc'
    }

    Breakup_shr_cptl = {
        'NO_ES_BEG' : 'byesns',
        'TOT_NOM_ES_BEG' : 'byestna',
        'TOT_PAID_ES_BEG' : 'byespua',
        'NO_ES_INC' : 'inesns',
        'TOT_NOM_ES_INC' : 'inestna',
        'TOT_PAID_ES_INC' : 'inespua',
        'TOT_PREM_ES_INC' : 'inesprm',
        'NO_ES_PUB' : 'pubesns',
        'TOT_NOM_ES_PUB' : 'pubestna',
        'TOT_PAID_ES_PUB' : 'pubespua',
        'TOT_PREM_ES_PUB' : 'pubesprm',
        'NO_ES_RIGHTS' : 'riesns',
        'TOT_NOM_ES_RIGHT' : 'riestna',
        'TOT_PAID_ES_RGHT' : 'riespua',
        'TOT_PREM_ES_RGHT' : 'riesprm',
        'NO_ES_BONUS' : 'biesns',
        'TOT_NOM_ES_BONUS' : 'biestna',
        'TOT_PAID_ES_BONS' : 'biespua',
        'TOT_PREM_ES_BONS' : 'biesprm',
        'NO_ES_PRIV' : 'ppesns',
        'TOT_NOM_ES_PRIV' : 'ppestna',
        'TOT_PAID_ES_PRIV' : 'ppespua',
        'TOT_PREM_ES_PRIV' : 'ppesprm',
        'NO_ES_ESOPS' : 'esopesns',
        'TOT_NOM_ES_ESOPS' : 'esopestna',
        'TOT_PAID_ES_ESOP' : 'esopespua',
        'TOT_PREM_ES_ESOP' : 'esopesprm',
        'NO_ES_SWT' : 'sesaesns',
        'TOT_NOM_ES_SWT' : 'sesaestna',
        'TOT_PAID_ES_SWT' : 'sesaespua',
        'TOT_PREM_ES_SWT' : 'sesaesprm',
        'NO_ES_CPS' : 'cpsesns',
        'TOT_NOM_ES_CPS' : 'cpsestna',
        'TOT_PAID_ES_CPS' : 'cpsespua',
        'TOT_PREM_ES_CPS' : 'cpsesprm',
        'NO_ES_COD' : 'cdbesns',
        'TOT_NOM_ES_COD' : 'cdbestna',
        'TOT_PAID_ES_COD' : 'cdbespua',
        'TOT_PREM_ES_COD' : 'cdbvesprm',
        'NO_ES_GDR_ADR' : 'gdresns',
        'TOT_NOM_GDR_ADR' : 'gdrestna',
        'TOT_PAID_GDR_ADR' : 'gdrespua',
        'TOT_PREM_GDR_ADR' : 'gdresprm',
        'OTHERS_ES_INC' : 'othes',
        'NO_ES_OT_I' : 'othesns',
        'TOT_NOM_ES_OT_I' : 'othestna',
        'TOT_PAID_ES_OT_I' : 'othespua',
        'TOT_PREM_ES_OT_I' : 'othesprm',
        'NO_ES_DEC' : 'decesns',
        'TOT_NOM_ES_DEC' : 'decestna',
        'TOT_PAID_ES_DEC' : 'decespua',
        'TOT_PREM_ES_DEC' : 'decesprm',
        'NO_ES_BB' : 'bbesns',
        'TOT_NOM_ES_BB' : 'bbestna',
        'TOT_PAID_ES_BB' : 'bbvpua',
        'TOT_PREM_ES_BB' : 'bbesprm',
        'NO_ES_FORF' : 'sfesns',
        'TOT_NOM_ES_FORF' : 'sfestna',
        'TOT_PAID_ES_FORF' : 'sfespua',
        'TOT_PREM_ES_FORF' : 'sfesprm',
        'NO_ES_RED' : 'rscesns',
        'TOT_NOM_ES_RED' : 'rscestna',
        'TOT_PAID_ES_RED' : 'rscespua',
        'TOT_PREM_ES_RED' : 'rscesprm',
        'OTHERS_ES_DEC' : 'ot1es',
        'NO_ES_OT_D' : 'ot1esns',
        'TOT_NOM_ES_OT_D' : 'ot1estna',
        'TOT_PAID_ES_OT_D' : 'ot1espua',
        'TOT_PREM_ES_OT_D' : 'ot1esprm',
        'NO_ES_END' : 'eyesns',
        'TOT_NOM_ES_END' : 'eyestna',
        'TOT_PAID_ES_END' : 'eyespua',

        'NO_PS_BEG' : 'bypsns',
        'TOT_NOM_PS_BEG' : 'bypstna',
        'TOT_PAID_PS_BEG' : 'bypspua',
        'NO_PS_INC' : 'inpsns',
        'TOT_NOM_PS_INC' : 'inpstna',
        'TOT_PAID_PS_INC' : 'inpspua',
        'TOT_PREM_PS_INC' : 'inpsprm',
        'NO_PS_ISS' : 'iospsns',
        'TOT_NOM_PS_ISS' : 'iospstna',
        'TOT_PAID_PS_ISS' : 'iospspua',
        'TOT_PREM_PS_ISS' : 'iospsprm',
        'NO_PS_RIFS' : 'rifspsns',
        'TOT_NOM_PS_RIFS' : 'rifspstna',
        'TOT_PAID_PS_RIFS' : 'rifspspua',
        'TOT_PREM_PS_RIFS' : 'rifspsprm',
        'OTHERS_PS_INC' : 'ot2ps',
        'NO_PS_OT_I' : 'ot2psns',
        'TOT_NOM_PS_OT_I' : 'ot2pstna',
        'TOT_PAID_PS_OT_I' : 'ot2pspua',
        'TOT_PREM_PS_OT_I' : 'ot2psprm',
        'NO_PS_DEC' : 'decpsns',
        'TOT_NOM_PS_DEC' : 'decpstna',
        'TOT_PAID_PS_DEC' : 'decpspua',
        'TOT_PREM_PS_DEC' : 'decpsprm',
        'NO_PS_REDM' : 'redpsns',
        'TOT_NOM_PS_REDM' : 'redpstna',
        'TOT_PAID_PS_REDM' : 'redpspua',
        'TOT_PREM_PS_REDM' : 'redpsprm',
        'NO_PS_FORF' : 'sfpsns',
        'TOT_NOM_PS_FORF' : 'sfpstna',
        'TOT_PAID_PS_FORF' : 'sfpspua',
        'TOT_PREM_PS_FORF' : 'sfpsprm',
        'NO_PS_RED' : 'rdspsns',
        'TOT_NOM_PS_RED' : 'rdspstna',
        'TOT_PAID_PS_RED' : 'rdspspua',
        'TOT_PREM_PS_RED' : 'rdspsprm',
        'OTHERS_PS_DEC' : 'ot3ps',
        'NO_PS_OT_D' : 'ot3psns',
        'TOT_NOM_PS_OT_D' : 'ot3pstna',
        'TOT_PAID_PS_OT_D' : 'ot3pspua',
        'TOT_PREM_PS_OT_D' : 'ot3psprm',
        'NO_PS_END' : 'eypsns',
        'TOT_NOM_PS_END' : 'eypstna',
        'TOT_PAID_PS_END' : 'eypspua'
    }

    Share_Debtrans = {
        'RB_DETAILS_PROV' : 'dbpcd',
        'RB_SEPARATE_SHET' : 'ssadt',
        'DATE_PREV_AGM' : 'dpagm',
        'DATE_REGISTRATN' : 'drgtr',
        'TYPE_OF_TRANSFR' : 'tyotr',
        'NUM_OF_SHARES' : 'nosdu',
        'AMT_PER_SHARE' : 'apsdu',
        'LEDGER_FOLIO_TFO' : 'lftfr',
        'TRANSFEROR_NAME' : 'tfrnm',
        'SURNAME_TRNSFERO' : 'tfrsn',
        'MIDDLE_NAME_TRFO' : 'tfrmn',
        'LEDGER_FOLIO_TRE' : 'lfttfe',
        'TRANSFEREE_NAME' : 'tfenm',
        'SURNAME_TRNSFREE' : 'tfesn',
        'MIDDLE_NAME_TRFE' : 'tfemn',
        'FIRST_NAME_TRFE' : 'tfefn'
    }

    Deb = {
        'NO_UNITS_NCD' : 'nuncd',
        'NOM_VAL_UNIT_NCD' : 'nvuncd',
        'TOTAL_VAL_NCD' : 'tvncd',
        'NO_UNITS_PCD' : 'nupcd',
        'NOM_VAL_UNIT_PCD' : 'nvupcd',
        'TOTAL_VAL_PCD' : 'tvpcd',
        'NO_UNITS_FCD' : 'nufcd',
        'NOM_VAL_UNIT_FCD' : 'nvufcd',
        'TOTAL_VAL_FCD' : 'tvfcd',
        'TOT_TOTAL_VAL' : 'ttv',

        'NCD_AT_BEG_YEAR' : 'obyncd',
        'NCD_INC_DUR_YEAR' : 'idyncd',
        'NCD_DEC_DUR_YEAR' : 'ddyncd',
        'NCD_AT_END_YEAR' : 'oeyncd',
        'PCD_AT_BEG_YEAR' : 'obypcd',
        'PCD_INC_DUR_YEAR' : 'idypcd',
        'PCD_DEC_DUR_YEAR' : 'ddypcd',
        'PCD_AT_END_YEAR' : 'oeypcd',
        'FCD_AT_BEG_YEAR' : 'obyfcd',
        'FCD_INC_DUR_YEAR' : 'idyfcd',
        'FCD_DEC_DUR_YEAR' : 'ddyfcd',
        'FCD_AT_END_YEAR' : 'oeyfcd'
    }

    Sec = {
        'TYPE_SECURITIES' : 'tos',
        'NO_SECURITIES' : 'ns',
        'NOM_VALUE_UNIT' : 'nveu',
        'NOM_VALUE' : 'tnv',
        'PAID_UP_VAL_UNIT' : 'pveu',
        'PAID_UP_VALUE' : 'tpv',
        'TOT_NO_SECURITY' : 'tns',
        'TOT_NOM_VAL' : 'ttnv',
        'TOT_PAID_UP_VAL' : 'ttpv'
    }

    Sh_hold_pat = {
        'NUM_ES_INDIAN' : 'iens',
        'PER_ES_INDIAN' : 'iep',
        'NUM_PS_INDIAN' : 'ipns',
        'PER_PS_INDIAN' : 'ipp',
        'NUM_ES_NRI' : 'nriens',
        'PER_ES_NRI' : 'nriep',
        'NUM_PS_NRI' : 'nripns',
        'PER_PS_NRI' : 'nripp',
        'NUM_ES_FN' : 'fnens',
        'PER_ES_FN' : 'fnep',
        'NUM_PS_FN' : 'fnpns',
        'PER_PS_FN' : 'fnpp',
        'NUM_ES_CENT_GOV' : 'cgens',
        'PER_ES_CENT_GOV' : 'cgep',
        'NUM_PS_CENT_GOV' : 'cgpns',
        'PER_PS_CENT_GOV' : 'cgpp',
        'NUM_ES_STAT_GOV' : 'sgens',
        'PER_ES_STAT_GOV' : 'sgep',
        'NUM_PS_STAT_GOV' : 'sgpns',
        'PER_PS_STAT_GOV' : 'sgpp',
        'NUM_ES_GOV_CMP' : 'gcens',
        'PER_ES_GOV_CMP' : 'gcep',
        'NUM_PS_GOV_CMP' : 'gcpns',
        'PER_PS_GOV_CMP' : 'gcpp',
        'NUM_ES_INS_CMP' : 'icens',
        'PER_ES_INS_CMP' : 'icep',
        'NUM_PS_INS_CMP' : 'icpns',
        'PER_PS_INS_CMP' : 'icpp',
        'NUM_ES_BANKS' : 'bens',
        'PER_ES_BANKS' : 'bep',
        'NUM_PS_BANKS' : 'bpns',
        'PER_PS_BANKS' : 'bpp',
        'NUM_ES_FI' : 'fiens',
        'PER_ES_FI' : 'fiep',
        'NUM_PS_FI' : 'fipns',
        'PER_PS_FI' : 'fipp',
        'NUM_ES_FI_INV' : 'fivens',
        'PER_ES_FI_INV' : 'fivep',
        'NUM_PS_FI_INV' : 'fivpns',
        'PER_PS_FI_INV' : 'fivpp',
        'NUM_ES_MF' : 'mfens',
        'PER_ES_MF' : 'mfep',
        'NUM_PS_MF' : 'mfpns',
        'PER_PS_MF' : 'mfpp',
        'IN_NS_VEN_CAP' : 'vcens',
        'IN_PS_VEN_CAP' : 'vcep',
        'FRGN_NS_VEN_CAP' : 'vcpns',
        'FRGN_PS_VEN_CAP' : 'vcpp',
        'NUM_ES_BODY_COP' : 'bcens',
        'PER_ES_BODY_COP' : 'bcep',
        'NUM_PS_BODY_COP' : 'bcpns',
        'PER_PS_BODY_COP' : 'bcpp',
        'NUM_ES_OTHR_SH' : 'oens',
        'PER_ES_OTHR_SH' : 'oep',
        'NUM_PS_OTHR_SH' : 'opns',
        'PER_PS_OTHR_SH' : 'opp',
        'NUM_ES_TOTAL' : 'tens',
        'PER_ES_TOTAL' : 'tep',
        'NUM_PS_TOTAL' : 'tpns',
        'PER_PS_TOTAL' : 'tpp',
    }

    Sh_hold_nonprom = {
        'NO_ES_INDIAN_PUB' : 'iens',
        'PE_ES_INDIAN_PUB' : 'iep',
        'NO_PS_INDIAN_PUB' : 'ipns',
        'PE_PS_INDIAN_PUB' : 'ipp',
        'NUM_ES_NRI_PUBC' : 'nriens',
        'PER_ES_NRI_PUBC' : 'nriep',
        'NUM_PS_NRI_PUBC': 'nripns',
        'PER_PS_NRI_PUBC' : 'nripp',
        'NUM_ES_FN_PUBC' : 'fnens',
        'PER_ES_FN_PUBC' : 'fnep',
        'NUM_PS_FN_PUBC' : 'fnpns',
        'PER_PS_FN_PUBC' : 'fnpp',
        'NO_ES_CENT_GOV_P' :  'cgens',
        'PE_ES_CENT_GOV_P' : 'cgep',
        'NUM_PS_CG_PUBC' : 'cgpns',
        'PER_PS_CG_PUBC' : 'cgpp',
        'NO_ES_STAT_GOV_P' : 'sgens',
        'PE_ES_STAT_GOV_P' : 'sgep',
        'NUM_PS_ST_GOV_P' : 'sgpns',
        'PER_PS_ST_GOV_P' : 'sgpp',
        'NO_ES_GOV_CMP_PB' : 'gcens',
        'PE_ES_GOV_CMP_PB' : 'gcep',
        'NUM_PS_GOV_C_PB' : 'gcpns',
        'PER_PS_GOV_C_PB' : 'gcpp',

        'NO_ES_INS_CMP_PB' : 'icens',
        'PE_ES_INS_CMP_PB' : 'icep',
        'NUM_PS_INS_C_PB' : 'icpns',
        'PER_PS_INS_C_PB' : 'icpp',
        'NO_ES_BANKS_PUBC' : 'bens',
        'PE_ES_BANKS_PUBC' : 'bep',
        'NUM_PS_BANKS_PB' : 'bpns',
        'PER_PS_BANKS_PB' : 'bpp',
        'NUM_ES_FI_PUBC' : 'fiens',
        'PER_ES_FI_PUBC' : 'fiep',
        'NUM_PS_FI_PUBC' : 'fipns',
        'PER_PS_FI_PUBC' : 'fipp',
        'NUM_ES_FI_INV_P' : 'fivens',
        'PER_ES_FI_INV_P' : 'fivep',
        'NUM_PS_FI_INV_P' : 'fivpns',
        'PER_PS_FI_INV_P' : 'fivpp',
        'NUM_ES_MF_PUBC' : 'mfens',
        'PER_ES_MF_PUBC' : 'mfep',
        'NUM_PS_MF_PUBC' : 'mfpns',
        'PER_PS_MF_PUBC' : 'mfpp',
        'NO_ES_VEN_CAP_PB' : 'vcens',
        'PE_ES_VEN_CAP_PB' : 'vcep',
        'NUM_PS_VEN_C_PB' : 'vcpns',
        'PER_PS_VEN_C_PB' : 'vcpp',
        'NO_ES_BODY_C_PUB' : 'bcens',
        'PE_ES_BODY_C_PUB' : 'bcep',
        'NUM_PS_BODY_C_P' : 'bcpns',
        'PER_PS_BODY_C_P' : 'bcpp',
        'NO_ES_OTHR_SH_PB' : 'oens',
        'PE_ES_OTHR_SH_PB' : 'oep',
        'NUM_PS_OT_SH_PB' : 'opns',
        'PER_PS_OT_SH_PB' : 'opp',
        'NO_ES_TOTAL_PUBC' : 'tens',
        'PE_ES_TOTAL_PUBC' : 'tep',
        'NUM_PS_TOTAL_PB' : 'tpns',
        'PER_PS_TOTAL_PB' : 'tpp'
    }

    Num_pro_mem_deb = {
        'NO_PROMOTER_BEG' : 'pboy',
        'NO_PROMOTER_END' : 'peoy',
        'NO_MEMBER_BEG' : 'mboy',
        'NO_MEMBER_END' : 'meoy',
        'NO_DEB_HLD_BEG' : 'dboy',
        'NO_DEB_HLD_END' : 'deoy'
    }

    Court_convened = {
        'TYPE_OF_MEETING' : 'tom',
        'DATE_OF_MEETING' : 'dom',
        'NO_MEMB_ENTITLED' : 'nmem',
        'NO_MEMB_ATTENDED' : 'nma',
        'PERCNT_TOT_SHARE' : 'ptsh'
    }

    Board = {
        'DATE_OF_MEETING' : 'dom',
        'TOT_NO_DIRECTORS' : 'ndadom',
        'NO_DIRS_ATTENDED' : 'nda',
        'PERCNT_ATTENDNCE' : 'pa'
    }

    Att_Dirt = {
        'DIN' : 'din',
        'NAME_OF_DIRECTOR' : 'nod',
        'NO_BRD_MTNG_EA' : 'bnomda',
        'NO_BRD_MTNG_ATND' : 'bnoma',
        'PERCNT_BRD_MTNG' : 'bpoa',
        'NO_COM_MTNG_EA' : 'cnomda',
        'NO_COM_MTNG_ATND' : 'cnoma',
        'PERCNT_COM_MTNG' : 'cpoa',
        'RB_ATTENDED_AGM' : 'wagm'
    }

    Rem_Man_Dirt = {
        'NAME' : 'nm',
        'DESIGNATION' : 'dg',
        'GROSS_SALARY' : 'gs',
        'COMMISSION' : 'cm',
        'STOCK_OPTION' : 'so',
        'OTHERS' : 'oth',
        'TOTAL_AMOUNT' : 'ta',
        'TOT_GROSS_SAL' : 'tgs',
        'TOT_COMMISSION' : 'tc',
        'TOT_STOCK_OPTION' : 'tso',
        'TOT_OTHERS' : 'toth',
        'TOTAL' : 'tl'
    }

    Rem_Oth_Dirt = {
        'NAME' : 'nm',
        'DESIGNATION' : 'dg',
        'GROSS_SALARY' : 'gs',
        'COMMISSION' : 'cm',
        'STOCK_OPTION' : 'so',
        'OTHERS' : 'oth',
        'TOTAL_AMOUNT' : 'ta',
        'TOT_GROSS_SAL' : 'tgs',
        'TOT_COMMISSION' : 'tc',
        'TOT_STOCK_OPTION' : 'tso',
        'TOT_OTHERS' : 'toth',
        'TOTAL' : 'tl'
    }

    Penalties = {
        'NAME_COMP_DIR_OF' : 'ncydo',
        'NAME_COURT_CONC' : 'ncca',
        'DATE_OF_ORDER' : 'do',
        'NAME_OF_THE_ACT' : 'noas',
        'DETAILS_PENALITY' : 'dop',
        'DETAILS_APPEAL' : 'doap'
    }

    Offences = {
        'NAME_COMP_DIR_OF' : 'ncydo',
        'NAME_COURT_CONC' : 'ncca',
        'DATE_OF_ORDER' : 'do',
        'NAME_OF_THE_ACT' : 'noao',
        'PARTICULARS_OFFE' : 'po',
        'AMOUNT_COMPOUNDN' : 'aoc'
    }
    extracted_data = extract_fields(xml_file_path, Regular)
    save_to_json(extracted_data, json_path, "Reg")

    extr = extract_tables(xml_file_path, Bus_act, "T_ZMCA_MGT_7A_S2")
    save_to_json(extr, json_path,'Bus_Act')
    
    extr = extract_tables(xml_file_path, Part_Asc_Comp, "T_ZMCA_MGT_7A_S3")
    save_to_json(extr, json_path,'Part_Asc_Comp')

    extr = extract_content_fromto(xml_file_path, Equ_shr_fixed, "TOT_NO_ES_A_CAP", "TOT_AMT_ES_P_CAP")
    save_to_json(extr, json_path,'Equity_Share_Fixed')

    extr = extract_content_fromto(xml_file_path, Pref_shr_fixed, "TOT_NO_PS_A_CAP", "TOT_AMT_PS_P_CAP")
    save_to_json(extr, json_path,'Pref_Share_Fixed')

    extr = extract_tables(xml_file_path, Equ_shr, "T_ZMCA_MGT7A_S4I_A")
    save_to_json(extr, json_path,'Equity_Shares_Dynamic')

    extr = extract_tables(xml_file_path, Pref_shr, "T_ZMCA_MGT7A_S4I_B")
    save_to_json(extr, json_path,'Pref_Shares_Dynamic')

    extracted_data = extract_fields(xml_file_path, Breakup_shr_cptl)
    save_to_json(extracted_data, json_path, "Breakup_shr_cptl")

    extr = extract_tables(xml_file_path, Share_Debtrans, "T_ZMCA_MGT7A_S4_II")
    save_to_json(extr, json_path,'Share_DebTrans_Details')

    extr = extract_content_fromto(xml_file_path, Deb, "NO_UNITS_NCD", "FCD_AT_END_YEAR")
    save_to_json(extr, json_path,'Debentures')

    extr = extract_tables(xml_file_path, Sec, "T_ZMCA_MGT7A_S4_IV")
    save_to_json(extr, json_path,'Securities')

    extr = extract_content_fromto(xml_file_path, Sh_hold_pat, "NUM_ES_INDIAN", "PER_PS_TOTAL")
    save_to_json(extr, json_path,'Shr_Hdg_Prom')

    extracted_data = extract_fields(xml_file_path, Sh_hold_nonprom)
    save_to_json(extracted_data, json_path, "Shr_Hdg_NonProm")

    extracted_data = extract_fields(xml_file_path, Num_pro_mem_deb)
    save_to_json(extracted_data, json_path, "Num_Pro_Mem_Deb")

    extr = extract_tables(xml_file_path, Court_convened, "T_ZMCA_MGT7A_S8_A")
    save_to_json(extr, json_path,'Court_Convened_Meetings')

    extr = extract_tables(xml_file_path, Board, "T_ZMCA_MGT7A_S8_B")
    save_to_json(extr, json_path,'Board_Meetings')

    extr = extract_tables(xml_file_path, Att_Dirt, "T_ZMCA_MGT7A_S8_C")
    save_to_json(extr, json_path,'Attd_Dir')

    extr = extract_tables(xml_file_path, Rem_Man_Dirt, "T_ZMCA_MGT7A_S9_A")
    save_to_json(extr, json_path,'Rem_Num_MgDt')

    extr = extract_tables(xml_file_path, Rem_Man_Dirt, "T_ZMCA_MGT7A_S9_B")
    save_to_json(extr, json_path,'Rem_Num_OthDt')

    extr = extract_tables(xml_file_path, Penalties, "T_ZMCA_MGT7A_S11_A")
    save_to_json(extr, json_path,'Penalties')

    extr = extract_tables(xml_file_path, Offences, "T_ZMCA_MGT7A_S11_B")
    save_to_json(extr, json_path,'Offences')

    print(f"\nData extracted and saved to {json_path}")