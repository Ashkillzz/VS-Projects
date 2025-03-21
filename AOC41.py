import xml.etree.ElementTree as ET
import re
import json
from datetime import datetime


def xml_to_dict(xml_file, det):      ## Takes xml file and custom made dictionary for assigning new key-value pairs in JSON file

    tree = ET.parse(xml_file)       
    root = tree.getroot()       ## Obtains root element of tree in root obj
    extracted_data = {}     ## Empty Dict to store key-value pairs based on custom mapping dict
    
    for xml_tag, json_key in det.items():        
        for element in root.iter(xml_tag):      ## Iterates through the entire XML tree
            text = element.text.replace('\n' , ' ').strip() if element.text else None       
            #tag1 = element.tag
            if json_key not in extracted_data:      ## To prevent overwriting of value field in case of duplicate keys 
                extracted_data[json_key] = text  ## To alter in-case duplicate entries hv to be included
                break

    return extracted_data


def extract_tables(xml_file, fields, header):   ## To extract from tables with dynamic size
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    records = []
    n = len(fields)

    for record in root.iter(header):
        for sub in record:
            count = 0
            sub_record = {}  # Create a single dictionary for this sub
            for xml_tag, json_key in fields.items():
                for child in sub:
                    if child.tag == xml_tag:
                        if child.text != None:
                            sub_record[json_key] = child.text.replace('\r',' ').strip() if child.text else None  # Add the key-value pair to the dictionary
                        else:
                            sub_record[json_key] = None
                            count += 1
                        break

            if count < n:
                records.append(sub_record)     

    return records


def xml_to_nested_dict(xml_file, nested_tag_key_mapping):
    
    result = {}
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Iterate through each group in the nested mapping
    for group_name, tag_key_mapping in nested_tag_key_mapping.items():
        result[group_name] = {}

        for json_key in tag_key_mapping.values():
            result[group_name][json_key] = None

        # Iterate through each element in the XML file
        for elem in root.iter():
            for xml_tag, json_key in tag_key_mapping.items():
                if elem.tag == xml_tag:
                    if elem.text:
                        result[group_name][json_key] = elem.text.strip()

    return result


def xml_to_dict_tables(xml_file, mapper, start, end):

    tree1 = ET.parse(xml_file)       
    root = tree1.getroot()   

    extracted_data2 = {}
    in_range = False

    for xml_tag, json_key in mapper.items():
        for elem in root.iter(xml_tag):

            if elem.tag == start or type(elem.tag) == datetime:
                extracted_data2[json_key] = elem.text
                in_range = True
                break

            elif elem.tag == end:
                if type(elem.text) == int:
                    num = float(elem.text)
                    extracted_data2[json_key] = "{:.2f}".format(num)
                else:
                    extracted_data2[json_key] = elem.text
                
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


def save_to_json(data, json_file, name):

    try:
        # Read existing content from the file
        with open(json_file, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file does not exist or is empty/invalid, initialize as an empty dictionary
        existing_data = {}

    if name == 'Nature_cat_NotArm':
            temp_dict = {'Nature_cat_NotArm' : data}
            existing_data["Num_MAT_NotArm"] = temp_dict

    elif name == 'Dur_Date_Amt_NotArm':
        temp_dict = {'Dur_Date_Amt_NotArm' : data}
        existing_data["Num_MAT_NotArm"].update(temp_dict)

    elif name == 'Nature_cat_IsArm':
        temp_dict = {'Nature_cat_IsArm' : data}
        existing_data["Num_MAT_Arm"] = temp_dict

    elif name == 'Dur_Date_Amt_IsArm':
        temp_dict = {'Dur_Date_Amt_IsArm' : data}
        existing_data["Num_MAT_Arm"].update(temp_dict)

    elif name not in existing_data:
        existing_data[name] = data

    # Write the updated data back to the file
    with open(json_file, 'w') as file:
        json.dump(existing_data, file, indent=4)


if __name__ == "__main__":

    xml_file_path = r'D:\Aswin\VS Projects\Form_AOC-4_All Yes Scenario\datasets.xml'   

    json_file_path = 'AOC4.json'      # Output JSON file path    
    
    Reg = {                                  
        'FUID': 'fn',
        'HI_AUTORIZEDCAP': 'acc',
        'HI_NOMEM' : 'nmm', 
        'CIN': 'cin', 
        'GLN' : 'gln',
        'HI_COMPANYNAME' : 'noc',
        'REG_OFFICE_ADDR' : 'roa',
        'EMAIL_ID_COMPANY' : 'eml',
        'FY_START_DATE' : 'fsd',
        'FY_END_DATE' : 'fed',
        'DATE_BOD_MEETING' : 'dbm',
        'NATURE_OF_FS' : 'nof',
        'RB_PROV_FIN_STMT' : 'rpfs',
        'RB_ADOPTED_ADJOU' : 'raa',
        'DATE_BOD_MEETIN1' : 'dbms134',
        'DATE_SIGNING_RFS' : 'dsrfs',
        'RB_AGM_HELD' : 'agmhd',
        'DATE_AGM' : 'dagm',
        'DUE_DATE_AGM' : 'ddagm',
        'RB_EXTN_FY_AGM' : 'exfy',
        'DDA_AFTER_EXTNSN' : 'ddge',
        'RB_COMP_SUBSIDRY' : 'cpissub',
        'CIN_HOLDING_COMP' : 'cinhc',
        'NAME_HOLDING_CMP' : 'nmhc',
        'PROVISION_PURSUA' : 'pvptsb',
        'RB_SUBSIDARY_CMP' : 'cphassub',
        'NUM_SUBSIDARY_CM' : 'nsubcy',
        'NUM_OF_AUDITORS' : 'naud',
        'RB_SCHEDULE_III' : 's3ca',
        'TYPE_OF_INDUSTRY' : 'toi',
        'RB_CONSOLIDATED' : 'csfsrq',
        'RB_COMP_BOOK_ACC' : 'cybkap',
        'RB_COST_RECORDS' : 'mtcrm',
        'RB_CSR_APPLICABL' : 'rca',
        'TURNOVER' : 'tnor',
        'NET_WORTH' : 'ntw',
        'AVG_NET_PROFIT' : 'anp',
        'PRESCRIBED_CSR_E' : 'prcsr',
        'TOTAL_AMT_SPENT' : 'tas',
        'AMOUNT_SPENT_LA' : 'asl',
        'NUM_CSR_ACTIVITY' : 'nca',
        'DETAILS_IMPLEMEN' : 'dimpay',
        'RB_RESP_CSR_COMM' : 'rrcc',
        'RB_COMPTRL_AUDTR' : 'cpsup',
        'RB_AUDTR_REPORT' : 'rar',
        'NUMBER_OF_QUALIF' : 'noq',
        'RB_COMP_AUDT_REP' : 'rcar',
        'RB_SECRETARIAL_A' : 'secat',
        'RB_DETAILED_DISC' : 'dtrs134'
    }

    Det_Sign_FS_BR = {      
        'Fin_Stmt_Signing' : {
            'DIN_PAN1' : 'dinfs1',
            'DATE_SIGNING_FS1' : 'dsfs1',
            'DIN_PAN2' : 'dinfs2',
            'DATE_SIGNING_FS2' : 'dsfs2',
            'DIN_PAN3' : 'dinfs3',
            'DATE_SIGNING_FS3' : 'dsfs3',
            'DIN_PAN4' : 'dinfs4',
            'DATE_SIGNING_FS4' : 'dsfs4',
            'DIN_PAN5' : 'dinfs5',
            'DATE_SIGNING_FS5' : 'dsfs5'
        },

        'Bd_Rpt_Signing' : {
            'DIN1' : 'dinbr1',
            'DATE_SIGNING_BR1' : 'dsbr1',
            'DIN2' : 'dinbr2',
            'DATE_SIGNING_BR2' : 'dsbr2',
            'DIN3' : 'dinbr3',
            'DATE_SIGNING_BR3' : 'dsbr3'    
        }
    }

    Subsidiary = {
        'CIN_SUBSIDARY_CM' : 'cinsy',
        'NAME_SUBSDRY_CMP' : 'nmsy',
        'PROVISION_PUR_C' : 'prov'
    }

    Aud_Det = {
        'IT_PAN' : 'panaud',
        'RB_CATEGORY_AUDT' : 'cgaud',
        'MEMBERSHIP_NUM_A' : 'mnaud',
        'SRN_ADT_1' : 'srnadt1',
        'NAME_AUDT_AUDTRF' : 'nmaud',
        'ADDRESS_LINE_I' : 'adln1',
        'ADDRESS_LINE_II' : 'adln2',
        'CITY' : 'cy',
        'STATE' : 'st',
        'COUNTRY' : 'ctry',
        'PIN_CODE' : 'pin',
        'NAME_OF_MEMBER' : 'nmmem',
        'MEMBERSHIP_NUMBR' : 'memnum'
    }

    ComSvs_ServProv = {
        'Postal_Addr_CS' : {
            'ADDRESS_LINE1' : 'addl1',
            'ADDRESS_LINE2' : 'addl2',
            'CITY' : 'cy',
            'STATE_UT' : 'stut',
            'PIN_CODE' : 'pin',
            'DISTRICT' : 'dt',
            'ISO_COUNTRY_CODE' : 'isocc',
            'COUNTRY' : 'cty',
            'PHONE_CODE' : 'phisd',
            'PHONE_NUMBER' : 'phno'
        },
        'Plr_Serv_Prov' : {
            'NAME_OF_SERVICE' : 'nosp',
            'INTERNET_PROT_AD' : 'ipasp',
            'LOCATION_OF_SERV' : 'locsp',
            'RB_BOOK_ACC_CLOU' : 'bpoc',
            'ADDRESS_PROVIDED' : 'addsp'
        }
    }

    Balance_sheet = {
        'DATE_CURR_REP' : 'dcr',
        'DATE_PREV_REP' : 'dpr',
        'SHARE_CAPITAL_CR' : 'scc',
        'SHARE_CAPITAL_PR' : 'scp',
        'RESERVE_SURPLUS1' : 'rsc',
        'RESERVE_SURPLUS2' : 'rsp',
        'MONEY_RECEIVD_CR' : 'mrc',
        'MONEY_RECEIVD_PR' : 'mrp',
        'SHARE_APP_MON_CR' : 'samc',
        'SHARE_APP_MON_PR' : 'samp',
        'LONG_TERM_BORR_C' : 'ltbc',
        'LONG_TERM_BORR_P' : 'ltbp',
        'DEFERRED_TL_CR' : 'dtlc',
        'DEFERRED_TL_PR' : 'dtlp',
        'OTHER_LNG_TRM_CR' : 'oltlc',
        'OTHER_LNG_TRM_PR' : 'oltlp',
        'LONG_TERM_PROV_C' : 'ltpc',
        'LONG_TERM_PROV_P' : 'ltpp',
        'SHORT_TERM_BOR_C' : 'stbc',
        'SHORT_TERM_BOR_P' : 'stbp',
        'TRADE_PAYABLES_C' : 'tpc',
        'TRADE_PAYABLES_P' : 'tpp',
        'OTHER_CURR_LIA_C' : 'oclc',
        'OTHER_CURR_LIA_P' : 'oclp',
        'SHORT_TERM_PRO_C' : 'stpc',
        'SHORT_TERM_PRO_P'  : 'stpp',
        'TOTAL_CURR_REP' : 'telc',
        'TOTAL_PREV_REP' : 'telp',
        'TANGIBLE_ASSET_C' : 'tac',
        'TANGIBLE_ASSET_P' : 'tap',
        'INTANGIBLE_AST_C' : 'iac',
        'INTANGIBLE_AST_P' : 'iap',
        'CAPITAL_WIP_CR' : 'cwc',
        'CAPITAL_WIP_PR' : 'cwp',
        'INTANGIBLE_AUD_C' : 'iadc',
        'INTANGIBLE_AUD_P' : 'iadp',
        'NON_CURR_INV_CR' : 'ncic',
        'NON_CURR_INV_PR' : 'ncip',
        'DEFERRED_TA_CR' : 'dtac',
        'DEFERRED_TA_PR' : 'dtap',
        'LT_LOANS_ADV_CR' : 'llac',
        'LT_LOANS_ADV_PR' : 'llap',
        'OTHER_NON_CA_CR' : 'oncac',
        'OTHER_NON_CA_PR' : 'oncap',
        'CURRENT_INV_CR' : 'cic',
        'CURRENT_INV_PR' : 'cip',
        'INVENTORIES_CR' : 'invc',
        'INVENTORIES_PR' : 'invp',
        'TRADE_RECEIV_CR' : 'trc',
        'TRADE_RECEIV_PR' : 'trp',
        'CASH_AND_EQU_CR' : 'caec',
        'CASH_AND_EQU_PR' : 'caep',
        'SHORT_TRM_LOA_CR' : 'stlac',
        'SHORT_TRM_LOA_PR' : 'stlap',
        'OTHER_CURR_CA_CR' : 'ocac',
        'OTHER_CURR_CA_PR' : 'ocap',
        'TOTAL_CURR_REP1' : 'toac',
        'TOTAL_PREV_REP1' : 'toap'
    }   

    Det_BS = {
        'Long_term_bor' : {
            'BONDS_DEBS_CR' : 'bdbc',
            'BONDS_DEBS_PR' : 'bdbp',
            'TERM_LOANS_FB_CR' : 'tlbc',
            'TERM_LOANS_FB_PR' : 'tlbp',
            'TERM_LOANS_FO_CR' : 'tlopc',
            'TERM_LOANS_FO_PR' : 'tlopp',
            'DEFERRED_PL_CR' : 'dfplc',
            'DEFERRED_PL_PR' : 'dfplp',
            'DEPOSITS_CR' : 'dpsc',
            'DEPOSITS_PR' : 'dpsp',
            'LOANS_ADV_RP_CR' : 'larpc',
            'LOANS_ADV_RP_PR' : 'larpp',  
            'LONG_TERM_MAT_CR' : 'ltmfoc',
            'LONG_TERM_MAT_PR' : 'ltmfop',
            'OTHER_LOA_CR' : 'olac',
            'OTHER_LOA_PR' : 'olap',
            'TOTAL_LT_BORR_CR' : 'tltbuc',
            'TOTAL_LT_BORR_PR' : 'tltbup',
            'TOT_AGGREGATE_CR' : 'taadc',
            'TOT_AGGREGATE_PR' : 'taadp',
        },
        'Short_term_bor' : {
            'LOAN_REPAY_B_CR' : 'lrdbc',
            'LOAN_REPAY_B_PR' : 'lrdbp',
            'LOAN_REPAY_OP_CR' : 'lrdopc',
            'LOAN_REPAY_OP_PR' : 'lrdopp',
            'LOANS_A_RP_ST_CR' : 'larpc',
            'LOANS_A_RP_ST_PR' : 'larpp',
            'DEPOSITS_ST_CR' : 'dpsc',
            'DEPOSITS_ST_PR' : 'dpsp',
            'OTH_LOANS_ADV_CR' : 'olac',
            'OTH_LOANS_ADV_PR' : 'olap',
            'TOTAL_ST_BORR_CR' : 'tstbuc',
            'TOTAL_ST_BORR_PR' : 'tstbup',
            'TOT_AGGREG_ST_CR' : 'taadc',
            'TOT_AGGREG_ST_PR' : 'taadp'
        },
        'Long_term_ln_adv_unsecured' : {
            'CAPT_ADVANCES_CR' : 'cladvc',
            'CAPT_ADVANCES_PR' : 'cladvp',
            'SECURITY_DEP_CR' : 'sydpsc',
            'SECURITY_DEP_PR' : 'sydpsp',
            'LOANS_ADV_ORP_CR' : 'latrpc',
            'LOANS_ADV_ORP_PR' : 'latrpp',
            'OTHER_LOANS_A_CR' : 'olac',
            'OTHER_LOANS_A_PR' : 'olap',
            'TOT_LT_LOAN_A_CR' : 'tltlac',
            'TOT_LT_LOAN_A_PR' : 'tltlap',
            'PROV_ALLOW_RP_CR' : 'pabdrpc',
            'PROV_ALLOW_RP_PR' : 'padbrpp',
            'PROV_ALLOW_OT_CR' : 'padboc',
            'PROV_ALLOW_OT_PR' : 'padbop',
            'NET_LT_LOA_CR' : 'nltlac',
            'NET_LT_LOA_PR' : 'nltlap',
            'LOANS_ADV_DUE_CR' : 'ladocyc',
            'LOANS_ADV_DUE_PR' : 'ladocyp'
        },
        'Long_term_ln_adv_doubtful' : {
            'CAPT_ADVANC_CR1' : 'cladv1c',
            'CAPT_ADVANC_PR1' : 'cladv1p',
            'SECURITY_DEP_CR1' : 'sydps1c',
            'SECURITY_DEP_PR1' : 'sydps1p',
            'LOANS_ADV_OR_CR1' : 'latrp1c',
            'LOANS_ADV_OR_PR1' : 'latrp1p',
            'OTHER_LOANS_CR1' : 'ola1c',
            'OTHER_LOANS_PR1' : 'ola1p',
            'TOT_LT_LOAN_CR1' : 'tltla1c',
            'TOT_LT_LOAN_PR1' : 'tltla1p',
            'PROV_ALLW_RP_CR1' : 'pabdrp1c',
            'PROV_ALLW_RP_PR1' : 'pabdrp1p',
            'PROV_ALLW_OT_CR1' : 'padbo1c',
            'PROV_ALLW_OT_PR1' : 'padbo1p',
            'NET_LT_LOA_CR1' : 'nltla1c',
            'NET_LT_LOA_PR1' : 'nltla1p',
            'LOAN_ADV_DUE_CR1' : 'ladocy1c',
            'LOAN_ADV_DUE_PR1' : 'ladocy1p'
        },
        'Trade_receivables' : {
            'SECURED_CG_ES_CR' : 'scge6c',
            'SECURED_CG_WS_CR' : 'scgw6c',
            'SECURED_CG_ES_PR' : 'scge6p',
            'SECURED_CG_WS_PR' : 'scgw6p',
            'UNSECURD_CG_ES_C' : 'ucge6c',
            'UNSECURD_CG_WS_C' : 'ucgw6c',
            'UNSECURD_CG_ES_P' : 'ucge6p',
            'UNSECURD_CG_WS_P' : 'ucgw6p',
            'DOUBTFUL_ES_CR' : 'dle6c',
            'DOUBTFUL_WS_CR' : 'dlw6c',
            'DOUBTFUL_ES_PR' : 'dle6p',
            'DOUBTFUL_WS_PR' : 'dlw6p',
            'TOTAL_TR_ES_CR' : 'ttre6c',
            'TOTAL_TR_WS_CR' : 'ttrw6c',
            'TOTAL_TR_ES_PR' : 'ttre6p',
            'TOTAL_TR_WS_PR' : 'ttrw6p',
            'LESS_PA_BAD_ES_C' : 'pabde6c',
            'LESS_PA_BAD_WS_C' : 'pabdw6c',
            'LESS_PA_BAD_ES_P' : 'pabde6p',
            'LESS_PA_BAD_WS_P' : 'pabdw6p',
            'NET_TRADE_R_ES_C' : 'ntre6c',
            'NET_TRADE_R_WS_C' : 'ntrw6c',
            'NET_TRADE_R_ES_P' : 'ntre6p',
            'NET_TRADE_R_WS_P' : 'ntrw6p',
            'DEBTS_DUE_ES_CR' : 'ddoce6c',
            'DEBTS_DUE_WS_CR' : 'ddocw6c',
            'DEBTS_DUE_ES_PR' : 'ddoce6p',
            'DEBTS_DUE_WS_PR' : 'ddocw6p'
        }
    }
    Fin_Param = {
        'AMOUNT_ISSUE_ALL' : 'aicrp',
        'SHARE_APP_MONEY' : 'samg',
        'SHARE_APP_MONEY1' : 'samgrp',
        'SHARE_APP_MONEY2' : 'samrrp',
        'SHARE_APP_MONEY3' : 'samrdf',
        'PAID_UP_CAPT_FC' : 'pcfc',
        'PAID_UP_CAPT_PER' : 'pcfcp',
        'PAID_UP_CAPT_FC1' : 'pcfhc',
        'PAID_UP_CAPT_PR1' : 'pcfhcp',
        'NUM_SHARES_BB' : 'nsbrp',
        'DEP_ACCEPTED_REN' : 'darrp',
        'DEP_MATURED_CLAI' : 'dmcnp',
        'DEP_MATURED_CLA1' : 'dmcn',
        'DEP_MATURED_CLA2' : 'dmn',
        'UNCLAIMED_M_DEB' : 'umd',
        'DEBENTURES_CLAIM' : 'dcn',
        'INTEREST_DEPOSIT' : 'idadn',
        'UNPAID_DIVIDEND' : 'updd',
        'INVESTMENT_SUBSD' : 'insbcy',
        'INVESTMENT_GOVT' : 'ingvcy',
        'CAPITAL_RESERVES' : 'clrs',
        'AMT_DUE_TRANSFER' : 'adt',
        'INTER_CORPORATE' : 'icd',
        'GROSS_VALUE' : 'gvt',
        'CAPITAL_SUBSDIES' : 'csg',
        'CALLS_UNPAID_DIR' : 'cudr',
        'CALLS_UNPAID_OTH' : 'cuoth',
        'FORFEITED_SHARES' : 'ffsh',
        'FORFEITED_SHAR_R' : 'ffshr',
        'BORROWING_FIA' : 'bwfia',
        'BORROWING_FC' : 'bwfc',
        'INTER_CORP_BORR' : 'icbs',
        'INTER_CORP_BORR1' : 'icbu',
        'COMMERCIAL_PAPER' : 'cp',
        'CONVERSION_WR_ES' : 'cwes',
        'CONVERSION_WR_PS' : 'cwps',
        'CONVERSION_WR_DE' : 'cwdb',
        'WARRANTS_ISSUED' : 'wrpfc',
        'WARRANTS_ISSUED1' : 'wrpinr',
        'DEFAULT_PAYMENT' : 'dpstbi',
        'DEFAULT_PAYMENT1' : 'dpltbi',
        'RB_OPERATING_LEA' : 'olcfl',
        'DETAILS_CONVERSN' : 'dtcv',
        'NET_WORTH_COMPAN' : 'nwc',
        'NUM_SHARE_HOLDRS' : 'nspp',
        'SECURED_LOAN' : 'scln',
        'GROSS_FIXD_ASSET' : 'gfa',
        'DEPRECIATN_AMORT' : 'dpa',
        'MISC_EXPENDITURE' : 'mea',
        'UNHEDGED_FE_EXP' : 'ufee'
    }

    Share_Capl_Rep_Pd = {
        'PUBLIC_ISSUE_ES' : 'pubes',
        'PUBLIC_ISSUE_PS' : 'pubps',
        'PUBLIC_ISSUE_TOT' : 'pubtl',
        'BONUS_ISSUE_ES' : 'bones',
        'BONUS_ISSUE_PS' : 'bonps',
        'BONUS_ISSUE_TOT' : 'bontl',
        'RIGHTS_ISSUE_ES' : 'rtes',
        'RIGHTS_ISSUE_PS' : 'rtps',
        'RIGHTS_ISSUE_TOT' : 'rttl',
        'PRIV_PLACEMENT_E' : 'prples',
        'PRIV_PLACEMENT_P' : 'prplps',
        'PRIV_PLACEMENT_T' : 'prpltl',
        'OTHR_PRI_PLAC_ES' : 'oppes',
        'OTHR_PRI_PLAC_PS' : 'oppps',
        'OTHR_PRI_PLAC_TO' : 'opptl',
        'PREF_ALLOTMENT_E' : 'prales',
        'PREF_ALLOTMENT_P' : 'pralps',
        'PREF_ALLOTMENT_T' : 'praltl',
        'OTHR_PREF_ALL_ES' : 'opaes',
        'OTHR_PREF_ALL_PS' : 'opaps',
        'OTHR_PREF_ALL_T' : 'opatl',
        'ESOP_ES' : 'esopes',
        'ESOP_PS' : 'esopps',
        'ESOP_TOTAL' : 'esoptl',
        'OTHER_ES' : 'othes',
        'OTHER_PS' : 'othps',
        'OTHER_TOTAL' : 'othtl',
        'TOTAL_SH_CAP_ES' : 'tsces',
        'TOTAL_SH_CAP_PS' : 'tscps',
        'TOTAL_SH_CAP_TOT' : 'tsctl' 
    }

    Profit_Loss = {
        'FROM_DATE_CR' : 'crpf',
        'TO_DATE_CR' : 'crpt',
        'FROM_DATE_PR' : 'prpf',
        'TO_DATE_PR' : 'prpt',
        'SALES_GOODS_CR' : 'dgmc',
        'SALES_GOODS_PR' : 'dgmp',
        'SALES_GOODS_T_CR' : 'dgtc',
        'SALES_GOODS_T_PR' : 'dgtp',
        'SALES_SUPPLY_CR' : 'dssc',
        'SALES_SUPPLY_PR' : 'dssp',
        'SALES_GOODS1_CR' : 'egmc',
        'SALES_GOODS1_PR' : 'egmp',
        'SALE_GOODS_T1_CR' : 'egtc',
        'SALE_GOODS_T1_PR' : 'egtp',
        'SALES_SUPPLY1_CR' : 'essc',
        'SALES_SUPPLY1_PR' : 'essp',
        'OTHER_INCOME_CR' : 'oic',
        'OTHER_INCOME_PR' : 'oip',
        'TOTAL_REVENUE_CR' : 'trc',
        'TOTAL_REVENUE_PR' : 'trp',
        'COST_MATERIAL_CR' : 'cmc',
        'COST_MATERIAL_PR' : 'cmp',
        'PURCHASE_STOCK_C' : 'pstc',
        'PURCHASE_STOCK_P' : 'pstp',
        'FINISHED_GOODS_C' : 'fgc',
        'FINISHED_GOODS_P' : 'fgp',
        'WORK_IN_PROG_CR' : 'wpc',
        'WORK_IN_PROG_PR' : 'wpp',
        'STOCK_IN_TRADE_C' : 'stc',
        'STOCK_IN_TRADE_P' : 'stp',
        'EMP_BENEFIT_EX_C' : 'ebec',
        'EMP_BENEFIT_EX_P' : 'ebep',
        'MANGERIAL_REM_CR' : 'mrc',
        'MANGERIAL_REM_PR' : 'mrp',
        'PAYMENT_AUDTRS_C' : 'pac',
        'PAYMENT_AUDTRS_P' : 'pap',
        'INSURANCE_EXP_CR' : 'iec',
        'INSURANCE_EXP_PR' : 'iep',
        'POWER_FUEL_CR' : 'pfc',
        'POWER_FUEL_PR' : 'pfp',
        'FINANCE_COST_CR' : 'fcc',
        'FINANCE_COST_PR' : 'fcp',
        'DEPRECTN_AMORT_C' : 'daec',
        'DEPRECTN_AMORT_P' : 'daep',
        'OTHER_EXPENSES_C' : 'oec',
        'OTHER_EXPENSES_P' : 'oep',
        'TOTAL_EXPENSES_C' : 'tec',
        'TOTAL_EXPENSES_P' : 'tep',
        'PROFIT_BEFORE_CR' : 'pbeetc',
        'PROFIT_BEFORE_PR' : 'pbeetp',
        'EXCEPTIONL_ITM_C' : 'excic',
        'EXCEPTIONL_ITM_P' : 'excip',
        'PROFIT_BEF_TAX_C' : 'pbetc',
        'PROFIT_BEF_TAX_P' : 'pbetp',
        'EXTRAORDINARY_CR' : 'extric',
        'EXTRAORDINARY_PR' : 'extrip',
        'PROF_B_TAX_7_8_C' : 'pbt78c',
        'PROF_B_TAX_7_8_P' : 'pbt78p',
        'CURRENT_TAX_CR' : 'ctec',
        'CURRENT_TAX_PR' : 'ctep',
        'DEFERRED_TAX_CR' : 'dtc',
        'DEFERRED_TAX_PR' : 'dtp',
        'PROF_LOSS_OPER_C' : 'plcoc',
        'PROF_LOSS_OPER_P' : 'plcop',
        'PROF_LOSS_DO_CR' : 'pldoc',
        'PROF_LOSS_DO_PR' : 'pldop',
        'TAX_EXPNS_DIS_CR' : 'tedoc',
        'TAX_EXPNS_DIS_PR' : 'tedop',
        'PROF_LOS_12_13_C' : 'pldo1213c',
        'PROF_LOS_12_13_P' : 'pldo1213p',
        'PROF_LOS_11_14_C' : 'pl1114c',
        'PROF_LOS_11_14_P' : 'pl1114p',
        'BASIC_BEFR_EI_CR' : 'bbec',
        'BASIC_BEFR_EI_PR' : 'bbep',
        'DILUTED_BEF_EI_C' : 'dbec',
        'DILUTED_BEF_EI_P' : 'dbep',
        'BASIC_AFTR_EI_CR' : 'baec',
        'BASIC_AFTR_EI_PR' : 'baep',
        'DILUTED_AFT_EI_C' : 'deaec',
        'DILUTED_AFT_EI_P' : 'deaep'
    }
    
    Det_Profit_loss = {
        'Earning_Fgn_Exc' : {
            'EXP_GOODS_FOB_CR' : 'egcc',
            'EXP_GOODS_FOB_PR' : 'egcp',
            'INTEREST_DIVD_CR' : 'iadc',
            'INTEREST_DIVD_PR' : 'iadp',
            'ROYALTY_CR' : 'ryc',
            'ROYALTY_PR' : 'ryp',
            'KNOW_HOW_CR' : 'khc',
            'KNOW_HOW_PR' : 'khp',
            'PROF_CONS_FEE_CR' : 'pacfc',
            'PROF_CONS_FEE_PR' : 'pacfp',
            'OTHR_INCOME_E_CR' : 'oic',
            'OTHR_INCOME_E_PR' : 'oip',
            'TOTAL_EARNG_FE_C' : 'tefec',
            'TOTAL_EARNG_FE_P' : 'tefep'
        },
        'Expenditure_Fgn_Exc' : {
            'RAW_MATERIAL_CR' : 'irmc',
            'RAW_MATERIAL_PR' : 'irmp',
            'COMPONENT_SP_CR' : 'icaspc',
            'COMPONENT_SP_PR' : 'icaspp',
            'CAPITAL_GOODS_CR' : 'icgc',
            'CAPITAL_GOODS_PR' : 'icgp',
            'ROYALTY_EXP_CR' : 'eryc',
            'ROYALTY_EXP_PR' : 'eryp',
            'KNOW_HOW_EXP_CR' : 'ekhc',
            'KNOW_HOW_EXP_PR' : 'ekhp',
            'PROF_CON_FEE_E_C' : 'epacfc',
            'PROF_CON_FEE_E_P' : 'epacfp',
            'INTEREST_EXP_CR' : 'einc',
            'INTEREST_EXP_PR' : 'einp',
            'OTHER_MATTERS_CR' : 'eomc',
            'OTHER_MATTERS_PR' : 'eomp',
            'DIVIDEND_PAID_CR' : 'edpc',
            'DIVIDEND_PAID_PR' : 'edpp',
            'TOT_EXP_FE_CR' : 'etefec',
            'TOT_EXP_FE_PR' : 'etefep'
        }
    }

    PF_Rep_Period = {
        'PROPOSED_DIVIDND' : 'pd',
        'PROPOSED_DIV_PER' : 'pdper',
        'BASIC_EARNING_PS' : 'esbs',
        'DILUTED_EARN_PS' : 'esdd',
        'INCOME_FOREIGN' : 'ifc',
        'EXPENDIT_FOREIGN' : 'efc',
        'REVENUE_SUBSIDIE' : 'rsgfga',
        'RENT_PAID' : 'rp',
        'CONSUMPTION_STOR' : 'cssp',
        'GROSS_VALUE_TRAN' : 'gvtrp',
        'BAD_DEBTS_RP' : 'bdrp'
    }

    Prin_Prd_Ser_Comp = {
        'PRODUCT_SERV_CC' : 'pscc',
        'DESC_PRODUCT_SER' : 'dpsc',
        'TURNOVR_PROD_SER' : 'tpsc',
        'HIGHEST_TO_PRD_S' : 'htpsc',
        'DESC_HIGH_TO_PRD' : 'dps',
        'TURNOVER_HIGHEST' : 'thcps'
    }

    CSR_Act = {
        'CSR_PROJECT_ACTV' : 'csrpj',
        'SECTOR_PROJ_COVR' : 'spjcov',
        'STATE_UT' : 'supj',
        'DISTRICT' : 'dispj',
        'AMOUNT_OUTLAY' : 'amtoly',
        'AMOUNT_SPENT_PRJ' : 'amtpj',
        'EXPENDITURE_ADM' : 'expadm',
        'MODE_AMOUNT_SPNT' : 'mamts'
    }  
    
    Nature_cat_NotArm = {
        'NAME_RELATED_PAR' : 'nmpty',
        'NATURE_OF_RELATN' : 'ntrel',
        'NATURE_OF_CONTRA' : 'ntcat'
    }

    Dur_Date_Amt_NotArm = {
        'DURATION_OF_CONT' : 'durcat',
        'DATE_OF_APPROVAL' : 'doab',
        'AMOUNT_PAID' : 'apd',
        'DATE_SPCL_RESOLT' : 'dsrgm'
    }

    Nature_cat_IsArm = {
        'NAME_RELATED_PAR' : 'nmpty',
        'NATURE_OF_RELATN' : 'ntrel',
        'NATURE_OF_CONTRA' : 'ntcat'
    }

    Dur_Date_Amt_IsArm = {
        'DURATION_OF_CONT' : 'durcat',
        'DATE_OF_APPROVAL' : 'doab',
        'AMOUNT_PAID' : 'apd'
    }
     
    Aud_Comts = {
        'AUDITORS_QUALIF' : 'AC',
        'DIRS_COMMENTS' : 'DC'
    } 

    Aud_Cmt_CARO = {
        'FIXED_ASSETS' : 'fa',
        'INVENTORIES' : 'ivs',
        'LOANS_GIVEN_COMP' : 'lgc',
        'ACCEPTANCE_PUB_D' : 'apd',
        'MAINTENANCE_CR' : 'mcr',
        'STATUTORY_DUES' : 'sd',
        'TERM_LOANS' : 'tl',
        'FRAUD_NOTICED' : 'fn',
        'OTHER_COMMENTS' : 'os'
    }

    Declaration = {
        'CVRN' : 'bdvrn',
        'DECLARATION_DATE' : 'bdcdt',
        'DESIGNATION' : 'Dg',
        'DIN_PAN_MEM_NUM' : 'Drin'
    }

    Cert_Prac_Prof = {
        'RB_CA_COA_CS' : 'Dg',
        'RB_ASSOC_FELLOW' : 'asfw',
        'MEMBERSHIP_NUM' : 'memnum'
    }


    extracted_data = xml_to_dict(xml_file_path, Reg)
    save_to_json(extracted_data, json_file_path,'Regular') 

    extracted_data = xml_to_nested_dict(xml_file_path, Det_Sign_FS_BR)
    save_to_json(extracted_data, json_file_path,'Det_Sign_FS_BR')

    extracted_data = extract_tables(xml_file_path, Subsidiary, "T_ZMCA_NCA_AOC4_S9")
    save_to_json(extracted_data, json_file_path,'Subsidiaries')

    extracted_data = extract_tables(xml_file_path, Aud_Det, "T_ZNCA_AOC_4_S10")
    save_to_json(extracted_data, json_file_path,'Aud_Det')

    extracted_data = xml_to_nested_dict(xml_file_path, ComSvs_ServProv)
    save_to_json(extracted_data, json_file_path,'ConSvs_ServProv')

    extracted_data = xml_to_dict_tables(xml_file_path, Balance_sheet, "DATE_CURR_REP", "TOTAL_PREV_REP1")
    save_to_json(extracted_data, json_file_path,'Bal_Sht') 

    extracted_data = xml_to_nested_dict(xml_file_path, Det_BS)
    save_to_json(extracted_data, json_file_path,'Det_BalSht')

    extracted_data = xml_to_dict(xml_file_path, Fin_Param)
    save_to_json(extracted_data, json_file_path,'Fin_Param') 

    extracted_data = xml_to_dict_tables(xml_file_path, Share_Capl_Rep_Pd,  "PUBLIC_ISSUE_ES", "TOTAL_SH_CAP_TOT")
    save_to_json(extracted_data, json_file_path,'Share_Capl_Rep_Pd')

    extracted_data = xml_to_dict_tables(xml_file_path, Profit_Loss, "FROM_DATE_CR", "DILUTED_AFT_EI_P")
    save_to_json(extracted_data, json_file_path,'Prof/Loss') 

    extracted_data = xml_to_nested_dict(xml_file_path, Det_Profit_loss)
    save_to_json(extracted_data, json_file_path,'Det_Profit_Loss')

    extracted_data = xml_to_dict_tables(xml_file_path, PF_Rep_Period, "PROPOSED_DIVIDND", "BAD_DEBTS_RP")
    save_to_json(extracted_data, json_file_path,'PF_Rep_Period')

    extracted_data = extract_tables(xml_file_path, Prin_Prd_Ser_Comp, "T_ZNCA_AOC_4_SII_4")
    save_to_json(extracted_data, json_file_path,'Prin_Prd_Ser_Comp')

    extracted_data = extract_tables(xml_file_path, CSR_Act, "T_ZNCA_AOC_4_SIII")
    save_to_json(extracted_data, json_file_path,'CSR_Activity') 

    extracted_data = extract_tables(xml_file_path, Nature_cat_NotArm, "T_ZNCA_AOC_4_SIV_1")
    save_to_json(extracted_data, json_file_path,'Nature_cat_NotArm')

    extracted_data = extract_tables(xml_file_path, Dur_Date_Amt_NotArm, "T_ZNCA_AOC_4_SIV_2")
    save_to_json(extracted_data, json_file_path,'Dur_Date_Amt_NotArm') 

    extracted_data = extract_tables(xml_file_path, Nature_cat_IsArm, "T_ZNCA_AOC_4_SIV_3")
    save_to_json(extracted_data, json_file_path,'Nature_cat_IsArm')

    extracted_data = extract_tables(xml_file_path, Dur_Date_Amt_IsArm, "T_ZNCA_AOC_4_SIV_4")
    save_to_json(extracted_data, json_file_path,'Dur_Date_Amt_IsArm')

    extracted_data = extract_tables(xml_file_path, Aud_Comts, "T_ZNCA_AOC_4_SV_II")
    save_to_json(extracted_data, json_file_path,'Aud_Comts')

    extracted_data = xml_to_dict(xml_file_path, Aud_Cmt_CARO)
    save_to_json(extracted_data, json_file_path,'CARO')

    extracted_data = xml_to_dict(xml_file_path, Declaration)
    save_to_json(extracted_data, json_file_path,'Declaration')

    extracted_data = xml_to_dict(xml_file_path, Cert_Prac_Prof)
    save_to_json(extracted_data, json_file_path,'Cert_Prac_Prof') 

    print(f"\nData extracted and saved to {json_file_path}")

