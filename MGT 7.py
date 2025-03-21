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

def extract_content_fromto(xml_file, fields, start, end):   ## To extract content from a start to end point
    tree = ET.parse(xml_file)
    root = tree.getroot()

    extracted_data2 = {}
    in_range = False

    for xml_tag, json_key in fields.items():
        for elem in root.iter(xml_tag):

            if elem.tag == start:
                extracted_data2[json_key] = str(float(elem.text))
                in_range = True
                break

            elif elem.tag == end:
                extracted_data2[json_key] = "{:.2f}".format(float(elem.text))
                
                return extracted_data2
                
        

            elif in_range and elem.tag not in (start, end):
                if elem.text ==  None:
                    extracted_data2[json_key] = None

                elif ('.' in  elem.text) and (re.fullmatch(r"-?\d+(\.\d+)?",elem.text)):
                    extracted_data2[json_key] = "{:.2f}".format(float(elem.text))

                else:
                    try: 
                        int(elem.text)
                        extracted_data2[json_key] = str(int(elem.text))

                    except ValueError:
                        extracted_data2[json_key] = elem.text
                
                break


def extract_tables(xml_file, fields, header):   ## To extract from tables(With "DATA" sub-field) of dynamic size
    
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
                                sub_records[json_key] = "{:.2f}".format(float(child.text))
                            else:
                                try: 
                                    int(child.text)
                                    sub_records[json_key] = str(int(child.text))

                                except ValueError:
                                    sub_records[json_key] = child.text

                        else:
                            sub_records[json_key] = None
                            count+=1                        
                        break

            if count < n:
                records.append(sub_records)
    
    return records


def extract_tables2(xml_file, fields, title):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    records = {}

    for record in root.iter(title):     ## To extract from tables(Direct children of root element) of dynamic size
        for xml_tag, json_key in fields.items():    
            for elem in record:
                if xml_tag == elem.tag and json_key not in records.keys():
                    if elem.text ==  None:
                        records[json_key] = None
                    elif ('.' in  elem.text) and (re.fullmatch(r"-?\d+(\.\d+)?",elem.text)):
                        records[json_key] = "{:.2f}".format(float(elem.text))
                    else:
                        try: 
                            int(elem.text)
                            records[json_key] = str(int(elem.text))

                        except ValueError:
                            records[json_key] = elem.text
                        
                    break

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
        temp_dict = {'Pref_Shares_Dynamic' : data}
        existing_data["Share_Capital"].update(temp_dict)

    elif name not in existing_data:
        existing_data[name] = data

    # Write the updated data back to the file
    with open(json_file, 'w') as file:
        json.dump(existing_data, file, indent=4)


if __name__ == "__main__":

    xml_file_path = r'D:\Aswin\VS Projects\Form MGT-7-2023-24_data.xml'

    json_path = "MGT7.json"

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
        'ISIN_ES' : 'isines',
        'DET_STOCK_SPLIT' : 'dtstsp',
        'TOT_TURNOVER' : 'to',
        'NET_WORTH_COMP' : 'nwc',
        'TOT_NO_SHARE_HLD' : 'tsp',
        'TOT_NO_SHR_HLD_P' : 'tsop',
        'TOT_NO_SH_PR_PUB' : 'tsppo',
        'NO_KMP' : 'ndkmp',
        'CHNGE_DIR_KMP_YR' : 'chdrkmp',
        'RB_COMP_COMPLAIN' : 'cpdsc',
        'IF_NO_REASONS' : 'ifno',
        'RB_COMPLETE_LIST' : 'lshdba',
        'NAME_COMP_SECR' : 'nmldcmp',
        'RB_ASSOC_FELLOW' : 'assoflw',
        'CERT_PRACTC_NUM' : 'ctprnum'
    }

    Hold_Subs_Asc = {
        'NAME_COMPANY' : 'noc',
        'CIN_FCRN' : 'cin',
        'HOLD_SUB_ASSOC' : 'hsajv',
        'PERCENT_SHARE' : 'psh'
    }

    Prin_Bus_act = {
        'MAIN_ACT_GRP_COD'  : 'magc',
        'DES_MAIN_ACT_GRP' : 'dmag',
        'BUSINESS_ACT_COD' : 'bac',
        'DES_BUSINESS_ACT' : 'dba',
        'PERCENT_TURN_OVR' : 'ptc'   
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
        'NO_ES_BEG_PHY' : 'byesphy',
        'NO_ES_BEG_DEMAT' : 'byesdem',
        'NO_ES_BEG' : 'byestl',
        'TOT_NOM_ES_BEG' : 'byesnom',
        'TOT_PAID_ES_BEG' : 'byespua',
        'NO_ES_INC_PHY' : 'inesphy',
        'NO_ES_INC_DEMAT' : 'inesdem',
        'NO_ES_INC' : 'inestl',
        'TOT_NOM_ES_INC' : 'inesnom',
        'TOT_PAID_ES_INC' : 'inespua',
        'TOT_PREM_ES_INC' : 'inesprm',
        'NO_ES_PUB_PHY' : 'pubesphy',
        'NO_ES_PUB_DEMAT' : 'pubesdem',
        'NO_ES_PUB' : 'pubestl',
        'TOT_NOM_ES_PUB' : 'pubesnom',
        'TOT_PAID_ES_PUB' : 'pubespua',
        'TOT_PREM_ES_PUB' : 'pubesprm',
        'NO_ES_RIGHTS_PHY' : 'riesphy',
        'NO_ES_RIGHTS_DEM' : 'riesdem',
        'NO_ES_RIGHTS' : 'riestl',
        'TOT_NOM_ES_RIGHT' : 'riesnom',
        'TOT_PAID_ES_RGHT' : 'riespua',
        'TOT_PREM_ES_RGHT' : 'riesprm',
        'NO_ES_BONUS_PHY' : 'biesphy',
        'NO_ES_BONUS_DEMA' : 'biesdem',
        'NO_ES_BONUS' : 'biestl',
        'TOT_NOM_ES_BONUS' : 'biesnom',
        'TOT_PAID_ES_BONS' : 'biespua',
        'TOT_PREM_ES_BONS' : 'biesprm',
        'NO_ES_PRIV_PHY' : 'ppesphy',
        'NO_ES_PRIV_DEMAT' : 'ppesdem',
        'NO_ES_PRIV' : 'ppestl',
        'TOT_NOM_ES_PRIV' : 'ppesnom',
        'TOT_PAID_ES_PRIV' : 'ppespua',
        'TOT_PREM_ES_PRIV' : 'ppesprm',
        'NO_ES_ESO_PHY' : 'esopesphy',
        'NO_ES_ESO_DEMAT' : 'esopesdem',
        'NO_ES_ESOPS' : 'esopestl',
        'TOT_NOM_ES_ESOPS' : 'esopesnom',
        'TOT_PAID_ES_ESOP' : 'esopespua',
        'TOT_PREM_ES_ESOP' : 'esopesprm',
        'NO_ES_SWT_PHY' : 'sesaesphy',
        'NO_ES_SWT_DEMAT' : 'sesaesdem',
        'NO_ES_SWT' : 'sesaestl',
        'TOT_NOM_ES_SWT' : 'sesaesnom',
        'TOT_PAID_ES_SWT' : 'sesaespua',
        'TOT_PREM_ES_SWT' : 'sesaesprm',
        'NO_ES_CPS_PHY' : 'cpsesphy',
        'NO_ES_CPS_DEMAT' : 'cpsesdem',
        'NO_ES_CPS' : 'cpsestl',
        'TOT_NOM_ES_CPS' : 'cpsesnom',
        'TOT_PAID_ES_CPS' : 'cpsespua',
        'TOT_PREM_ES_CPS' : 'cpsesprm',
        'NO_ES_COD_PHY' : 'cdbesphy',
        'NO_ES_COD_DEMAT' : 'cdbesdem',
        'NO_ES_COD' : 'cdbvtl',
        'TOT_NOM_ES_COD' : 'cdbesnom',
        'TOT_PAID_ES_COD' : 'cdbespua',
        'TOT_PREM_ES_COD' : 'cdbesprm',
        'NO_ES_GDRADR_PHY' : 'gdresphy',
        'NO_ES_GDRADR_DEM' : 'gdresdem',
        'NO_ES_GDR_ADR' : 'gdrestl',
        'TOT_NOM_GDR_ADR' : 'gdresnom',
        'TOT_PAID_GDR_ADR' : 'gdrespua',
        'TOT_PREM_GDR_ADR' : 'gdresprm',
        'NO_ES_OT_I_PHY' : 'othvphy',
        'NO_ES_OT_I_DEMAT' : 'othesdem',
        'NO_ES_OT_I' : 'othestl',
        'TOT_NOM_ES_OT_I' : 'othesnom',
        'TOT_PAID_ES_OT_I' : 'othespua',
        'TOT_PREM_ES_OT_I' : 'othesprm',
        'NO_ES_DEC_PHY' : 'decesphy',
        'NO_ES_DEC_DEMAT' : 'decesdem',
        'NO_ES_DEC' : 'decestl',
        'TOT_NOM_ES_DEC' : 'decesnom',
        'TOT_PAID_ES_DEC' : 'decespua',
        'TOT_PREM_ES_DEC' : 'decesprm',
        'NO_ES_BB_PHY' : 'bbsesphy',
        'NO_ES_BB_DEMAT' : 'bbsesdem',
        'NO_ES_BB' : 'bbsestl',
        'TOT_NOM_ES_BB' : 'bbsesnom',
        'TOT_PAID_ES_BB' : 'bbsespua',
        'TOT_PREM_ES_BB' : 'bbsesprm',
        'NO_ES_FORF_PHY' : 'sfesphy',
        'NO_ES_FORF_DEMAT' : 'sfesdem',
        'NO_ES_FORF' : 'sfvtl',
        'TOT_NOM_ES_FORF' : 'sfesnom',
        'TOT_PAID_ES_FORF' : 'sfespua',
        'TOT_PREM_ES_FORF' : 'sfesprm',
        'NO_ES_RED_PHY' : 'rscesphy',
        'NO_ES_RED_DEMAT' : 'rscesdem',
        'NO_ES_RED' : 'rscestl',
        'TOT_NOM_ES_RED' : 'rscesnom',
        'TOT_PAID_ES_RED' : 'rscespua',
        'TOT_PREM_ES_RED' : 'rscesprm',
        'NO_ES_OT_D_PHY' : 'ot1esphy',
        'NO_ES_OT_D_DEMAT' : 'ot1esdem',
        'NO_ES_OT_D' : 'ot1estl',
        'TOT_NOM_ES_OT_D' : 'ot1esnom',
        'TOT_PAID_ES_OT_D' : 'ot1espua',
        'TOT_PREM_ES_OT_D' : 'ot1esprm',
        'NO_ES_END_PHY' : 'eyesphy',
        'NO_ES_END_DEMAT' : 'eyesdem',
        'NO_ES_END' : 'eyestl',
        'TOT_NOM_ES_END' : 'eyesnom',
        'TOT_PAID_ES_END' : 'eyespua',


        'NO_PS_BEG_PHY' : 'bypsphy',
        'NO_PS_BEG_DEM' : 'bypsdem',
        'NO_PS_BEG' : 'bypstl',
        'TOT_NOM_PS_BEG' : 'bypsnom',
        'TOT_PAID_PS_BEG' : 'bypspua',
        'NO_PS_INC_PHY' : 'inpsphy',
        'NO_PS_INC_DEM' : 'inpsdem',
        'NO_PS_INC' : 'inpstl',
        'TOT_NOM_PS_INC' : 'inpsnom',
        'TOT_PAID_PS_INC' : 'inpspua',
        'TOT_PREM_PS_INC' : 'inpsprm',
        'NO_PS_ISS_PHY' : 'iospsphy',
        'NO_PS_ISS_DEM' : 'iospsdem',
        'NO_PS_ISS' : 'iospstl',
        'TOT_NOM_PS_ISS' : 'iospsnom',
        'TOT_PAID_PS_ISS' : 'iospspua',
        'TOT_PREM_PS_ISS' : 'iospsprm',
        'NO_PS_RIFS_PHY' : 'rifspsphy',
        'NO_PS_RIFS_DEM' : 'rifspsdem',
        'NO_PS_RIFS' : 'rifspstl',
        'TOT_NOM_PS_RIFS' : 'rifspsnom',
        'TOT_PAID_PS_RIFS' : 'rifspspua',
        'TOT_PREM_PS_RIFS' : 'rifspsprm',
        'NO_PS_OT_I_PHY' : 'ot2psphy',
        'NO_PS_OT_I_DEM' : 'ot2psdem',
        'NO_PS_OT_I' : 'ot2pstl',
        'TOT_NOM_PS_OT_I' : 'ot2psnom',
        'TOT_PAID_PS_OT_I' : 'ot2pspua',
        'TOT_PREM_PS_OT_I' : 'ot2psprm',
        'NO_PS_DEC_PHY' : 'decpsphy',
        'NO_PS_DEC_DEM' : 'decpsdem',
        'NO_PS_DEC' : 'decpstl',
        'TOT_NOM_PS_DEC' : 'decpsnom',
        'TOT_PAID_PS_DEC' : 'decpspua',
        'TOT_PREM_PS_DEC' : 'decpsprm',
        'NO_PS_REDM_PHY' : 'redpsphy',
        'NO_PS_REDM_DEM' : 'redpsdem',
        'NO_PS_REDM' : 'redpstl',
        'TOT_NOM_PS_REDM' : 'redpsnom',
        'TOT_PAID_PS_REDM' : 'redpspua',
        'TOT_PREM_PS_REDM' : 'redpsprm',
        'NO_PS_FORF_PHY' : 'sfpsphy',
        'NO_PS_FORF_DEM' : 'sfpsdem',
        'NO_PS_FORF' : 'sfpstl',
        'TOT_NOM_PS_FORF' : 'sfpsnom',
        'TOT_PAID_PS_FORF' : 'sfpspua',
        'TOT_PREM_PS_FORF' : 'sfpsprm',
        'NO_PS_RED_PHY' : 'rdspsphy',
        'NO_PS_RED_DEM' : 'rdspsdem',
        'NO_PS_RED' : 'rdspstl',
        'TOT_NOM_PS_RED' : 'rdspsnom',
        'TOT_PAID_PS_RED' : 'rdspspua',
        'TOT_PREM_PS_RED' : 'rdspsprm',
        'NO_PS_OT_D_PHY' : 'ot3psphy',
        'NO_PS_OT_D_DEM' : 'ot3psdem',
        'NO_PS_OT_D' : 'ot3pstl',
        'TOT_NOM_PS_OT_D' : 'ot3psnom',
        'TOT_PAID_PS_OT_D' : 'ot3pspua',
        'TOT_PREM_PS_OT_D' : 'ot3psprm',
        'NO_PS_END_PHY' : 'eypsphy',
        'NO_PS_END_DEM' : 'eypsdem',
        'NO_PS_END' : 'eypstl',
        'TOT_NOM_PS_END' : 'eypsnom',
        'TOT_PAID_PS_END' : 'eypspua'
    }

    Det_Stock_Split = {
        'BFS_NO_SHARES_1' : 'bsnos1',
        'BFS_NO_SHARES_2' : 'bsnos2',
        'BFS_NO_SHARES_3' : 'bsnos3',
        'BFS_FV_SHARE_1' : 'bsfvs1',
        'BFS_FV_SHARE_2' : 'bsfvs2',
        'BFS_FV_SHARE_3' : 'bsfvs3',
        'AFS_NO_SHARES_1' : 'asnos1',
        'AFS_NO_SHARES_2' : 'asnos2',
        'AFS_NO_SHARES_3' : 'asnos3',
        'AFS_FV_SHARE_1' : 'asfvs1',
        'AFS_FV_SHARE_2' : 'asfvs2',
        'AFS_FV_SHARE_3' : 'asfvs3'
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

    Num_pro_mem_deb = {
        'NO_PROMOTER_BEG' : 'pboy',
        'NO_PROMOTER_END' : 'peoy',
        'NO_MEMBER_BEG' : 'mboy',
        'NO_MEMBER_END' : 'meoy',
        'NO_DEB_HLD_BEG' : 'dboy',
        'NO_DEB_HLD_END' : 'deoy'
    }

    Comp_BOD = {
        'NO_ED_PROM_BEG' : 'bpe',
        'NO_NED_PROM_BEG' : 'bpne',
        'NO_ED_PROM_END' : 'epe',
        'NO_NED_PROM_END' : 'epne',
        'PS_ED_PROM_END' : 'pspe',
        'PS_NED_PROM_END' : 'pspne',
        'NO_ED_NPROM_BEG' : 'bnpe',
        'NO_NED_NPROM_BEG' : 'bnpne',
        'NO_ED_NPROM_END' : 'enpe',
        'NO_NED_NPROM_END' : 'enpne',
        'PS_ED_NPROM_END' : 'psnpe',
        'PS_NED_NPROM_END' : 'psnpne',
        'NO_ED_N_IND_BEG' : 'bnie',
        'NO_NED_N_IND_BEG' : 'bnine',
        'NO_ED_N_IND_END'  : 'enie',
        'NO_NED_N_IND_END' : 'enine',
        'PS_ED_N_IND_END' : 'psnie',
        'PS_NED_N_IND_END' : 'psnine',
        'NO_ED_IND_BEG' : 'bie',
        'NO_NED_IND_BEG' : 'bine',
        'NO_ED_IND_END' : 'eie',
        'NO_NED_IND_END' : 'eine',
        'PS_ED_IND_END' : 'psie',
        'PS_NED_IND_END' : 'psine',
        'NO_ED_NDR_BEG' : 'bnde',
        'NO_NED_NDR_BEG' : 'bndne',
        'NO_ED_NDR_END' : 'ende',
        'NO_NED_NDR_END' : 'endne',
        'PS_ED_NDR_END' : 'psnde',
        'PS_NED_NDR_END' : 'psndne',
        'NO_ED_B_FI_BEG' : 'bbfie',
        'NO_NED_B_FI_BEG' : 'bbfine',
        'NO_ED_B_FI_END' : 'ebfie',
        'NO_NED_B_FI_END' : 'ebfine',
        'PS_ED_B_FI_END' : 'psbfie',
        'PS_NED_B_FI_END' : 'psbfine',
        'NO_ED_INV_BEG' : 'biie',
        'NO_NED_INV_BEG'  : 'biine',
        'NO_ED_INV_END' : 'eiie',
        'NO_NED_INV_END' : 'eiine',
        'PS_ED_INV_END' : 'psiie',
        'PS_NED_INV_END' : 'psiine',
        'NO_ED_GOV_BEG' : 'bge',
        'NO_NED_GOV_BEG' : 'bgne',
        'NO_ED_GOV_END' : 'ege',
        'NO_NED_GOV_END' : 'egne',
        'PS_ED_GOV_END' : 'psge',
        'PS_NED_GOV_END' : 'psgne',
        'NO_ED_SSH_BEG' : 'bsshe',
        'NO_NED_SSH_BEG' : 'bsshne',
        'NO_ED_SSH_END' : 'esshe',
        'NO_NED_SSH_END' : 'esshne',
        'PS_ED_SSH_END' : 'pssshe',
        'PS_NED_SSH_END' : 'pssshne',
        'NO_ED_OTH_BEG': 'boe',
        'NO_NED_OTH_BEG' : 'bone',
        'NO_ED_OTH_END' : 'eoe',
        'NO_NED_OTH_END' : 'eone',
        'PS_ED_OTH_END' : 'psoe',
        'PS_NED_OTH_END' : 'psone',
        'TOT_NO_ED_BEG' : 'bte',
        'TOT_NO_NED_BEG' : 'btne',
        'TOT_NO_ED_END' : 'ete',
        'TOT_NO_NED_END' : 'etne',
        'TOT_PS_ED_END' : 'pste',
        'TOT_PS_NED_END' : 'pstne'
    }

    Det_drkmp_clsyr = {
        'NAME' : 'nm',
        'DIN_PAN' : 'din',
        'DESIGNATION' : 'dg',
        'NO_OF_EQUITY_SHR' : 'nes',
        'DATE_OF_CESSATN' : 'doces'
    }

    Det_drkmp_duryr = {
        'NAME' : 'nm',
        'DIN_PAN' : 'din',
        'DESIGNATION' : 'dgb',
        'DATE_APP_CD_CESS' : 'dacdc',
        'NATURE_OF_CHANGE' : 'natoc'
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
        'PER_PS_TOTAL' : 'tpp'
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

    Committee = {
        'TYPE_OF_MEETING' : 'tom',
        'DATE_OF_MEETING' : 'dom',
        'TOT_NO_MEMBERS' : 'tmdom',
        'NO_MEMB_ATTENDED' : 'nma',
        'PERCNT_TOT_SHARE' : 'pa'
    }

    Att_Dirt = {
        'NAME_OF_DIRECTOR' : 'nod',
        'NO_BRD_MTNG_EA' : 'bnomda',
        'NO_BRD_MTNG_ATND' : 'bnoma',
        'PERCNT_BRD_MTNG' : 'bpoa',
        'NO_COM_MTNG_EA' : 'cnomda',
        'NO_COM_MTNG_ATND' : 'cnoma',
        'PERCNT_COM_MTNG' : 'cpoa',
        'RB_ATTENDED_AGM' : 'wagm'
    }

    Rem = {
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
        'TOTAL' : 'tlamt'
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

    Declaration = {
        'CVRN' : 'bdvrn',
        'DATE_DECLARATION' : 'bdcdt',
        'DIN_OF_DIRECTOR' : 'dindr',
        'RB_COMP_SEC_CSP' : 'csocsip',
        'MEMBERSHIP_NUM' : 'memno',
        'CERT_PRACTC_NUM1' : 'crtpno'
    }

    extracted_data = extract_fields(xml_file_path, Regular)
    save_to_json(extracted_data, json_path, 'Regular')  

    extr = extract_tables(xml_file_path, Prin_Bus_act, "T_ZNCA_MGT_7_S2")
    save_to_json(extr, json_path,'Business_Activities')  

    extr = extract_tables(xml_file_path, Hold_Subs_Asc, "T_ZNCA_MGT_7_S3")
    save_to_json(extr, json_path,'Hold_Subs_Asc') 

    extr = extract_content_fromto(xml_file_path, Equ_shr_fixed, "TOT_NO_ES_A_CAP", "TOT_AMT_ES_P_CAP")
    save_to_json(extr, json_path,'Equity_Share_Fixed')

    extr = extract_content_fromto(xml_file_path, Pref_shr_fixed, "TOT_NO_PS_A_CAP", "TOT_AMT_PS_P_CAP")
    save_to_json(extr, json_path,'Pref_Share_Fixed')

    extr = extract_tables(xml_file_path, Equ_shr, "T_ZNCA_MGT_7_S4I_A")
    save_to_json(extr, json_path,'Equity_Shares_Dynamic')  
    
    extr = extract_tables(xml_file_path, Pref_shr, "T_ZNCA_MGT_7_S4I_B")
    save_to_json(extr, json_path,'Pref_Shares_Dynamic')  

    extracted_data = extract_fields(xml_file_path, Breakup_shr_cptl)
    save_to_json(extracted_data, json_path, 'Breakup of Share Capital')

    extr = extract_tables(xml_file_path, Det_Stock_Split, "T_ZNCA_MGT_7_S4_II")
    save_to_json(extr, json_path,'Det_Stock_Split')

    extr = extract_tables(xml_file_path, Share_Debtrans, "T_ZNCA_MGT7_S4_III")
    save_to_json(extr, json_path,'Share_DebTrans_Details')

    extr = extract_content_fromto(xml_file_path, Deb, "NO_UNITS_NCD", "FCD_AT_END_YEAR")
    save_to_json(extr, json_path,'Debentures')

    extr = extract_tables(xml_file_path, Sec, "T_ZNCA_MGT_7_S4_V")
    save_to_json(extr, json_path,'Securities')

    extr = extract_content_fromto(xml_file_path, Sh_hold_pat, "NUM_ES_INDIAN", "PER_PS_TOTAL")
    save_to_json(extr, json_path,'Shr_Hdg_Prom')

    extr = extract_tables2(xml_file_path, Sh_hold_nonprom, "ZMCA_NCA_MGT7_II")
    save_to_json(extr, json_path,'Shr_Hdg_NonProm')

    extracted_data = extract_fields(xml_file_path, Num_pro_mem_deb)
    save_to_json(extracted_data, json_path, "Num_Pro_Mem_Deb")  

    extr = extract_content_fromto(xml_file_path, Comp_BOD, "NO_ED_PROM_BEG", "TOT_PS_NED_END")
    save_to_json(extr, json_path,'Comp_Of_BOD')

    extr = extract_tables(xml_file_path, Det_drkmp_clsyr, "T_ZNCA_MGT_7_S8_B1")
    save_to_json(extr, json_path,'Det_drkmp_clsyr')

    extr = extract_tables(xml_file_path, Det_drkmp_duryr, "T_ZNCA_MGT_7_S8_B2")
    save_to_json(extr, json_path,'Det_drkmp_duryr')

    extr = extract_tables(xml_file_path, Court_convened, "T_ZNCA_MGT_7_S9_A")
    save_to_json(extr, json_path,'Court_Convened_Meetings')

    extr = extract_tables(xml_file_path, Board, "T_ZNCA_MGT_7_S9_B")
    save_to_json(extr, json_path,'Board_Meetings')

    extr = extract_tables(xml_file_path, Committee, "T_ZNCA_MGT_7_S9_C")
    save_to_json(extr, json_path,'Committee_Meetings')

    extr = extract_tables(xml_file_path, Att_Dirt, "T_ZNCA_MGT_7_S9_D")
    save_to_json(extr, json_path,'Att_dir')

    extr = extract_tables(xml_file_path, Rem, "T_ZNCA_MGT_7_S10_3")
    save_to_json(extr, json_path,'Rem_Other_Dirt')

    extr = extract_tables(xml_file_path, Rem, "T_ZNCA_MGT_7_S10_2")
    save_to_json(extr, json_path,'Rem_CEO_CFO_CS')

    extr = extract_tables(xml_file_path, Rem, "T_ZNCA_MGT_7_S10_1")
    save_to_json(extr, json_path,'Rem_MD_WTD')

    extr = extract_tables(xml_file_path, Penalties, "T_ZNCA_MGT_7_S12_A")
    save_to_json(extr, json_path,'Penalties')

    extr = extract_tables(xml_file_path, Offences, "T_ZNCA_MGT_7_S12_B")
    save_to_json(extr, json_path,'Offences')

    extracted_data = extract_fields(xml_file_path, Declaration)
    save_to_json(extracted_data, json_path, 'Declaration')

    print(f"\nData extracted and saved to {json_path}")