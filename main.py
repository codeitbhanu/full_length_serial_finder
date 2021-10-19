# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# imports
import pyodbc
import pandas as pd



# connect to db
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
driver = "{ODBC Driver 17 for SQL Server}"
server = "172.20.10.149\PRODUCTION"
database = "stb_production"
username = "Neo.Tech"
password = "Password357"
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
conn = pyodbc.connect("DRIVER=" + driver
                      + ";SERVER=" + server
                      + ";DATABASE=" + database
                      + ";UID=" + username
                      + ";PWD=" + password)
cursor = conn.cursor()



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
filename = 'BGA Rework - 3136 Units.xlsx'
product = '4138'
pallet_col = 'Pallet 4'
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


excel_data = pd.read_excel('BGA Rework - 3136 Units.xlsx')
# Read the values of the file in the dataframe
df = pd.DataFrame(excel_data, columns=[pallet_col])
# Print the content
# print("The content of the file is:\n", df)



stb_find_str = '\''
stb_find_list = []

stb_found_dict = {}

pallet_stbs = df.iterrows()

# print(df.to_numpy().flatten())
pallet_stbs_list = df.to_numpy().flatten()

print(f'{pallet_col} has {len(pallet_stbs_list)} stbs')

# TEST PARAMS
TEST_FLAG = False
TEST_COUNT = 0
TEST_ITERATION = 7  # This is test run limit for running over a sample of data

for stb_num_short in pallet_stbs_list:
    if (TEST_FLAG and TEST_COUNT < TEST_ITERATION):
        print(f'--TEST_COUNT-- {TEST_COUNT}')
        TEST_COUNT += 1
    elif (TEST_FLAG):
        break
    # print(f'{stb_num_short}')
    # time.sleep(1)
    stb_num_full_temp = ''
    for row in cursor.execute(f'''SELECT stb_num FROM stb_production.dbo.production_event
    WHERE stb_num LIKE \'{stb_num_short}%\''''):
        # print(f'>> {row.stb_num}')
        stb_find_str = stb_find_str + row.stb_num + '\',\''
        stb_num_full_temp = row.stb_num.strip()

    stb_found_dict[stb_num_short] = {
        "key_word": stb_num_short,
        "stb_num": stb_num_full_temp or 'NOT FOUND',
        "cdsn_iuc": 'NOT FOUND',
        "pcb_num": 'NOT FOUND'
    }



# Removes last 2 characters from string
if(stb_find_str.endswith(',\'')):
    stb_find_str = stb_find_str[:-2]

# TODO: improve, merge all above stb_nums with ''
print(f'''\n{"KEY_WORD"}\t\t{"STB_NUM"}\t\t\t{"IUC_NUM"}\t\t\t{"PCB_NUM"}''')
for innerrow in cursor.execute(f'''SELECT stb_num, cdsn_iuc, pcb_num FROM stb_production.dbo.production_event
                                    INNER JOIN
                                    device_state_dsd_{product} ON production_event.id_production_event = device_state_dsd_{product}.id_production_event
                                    WHERE        stb_num IN ({stb_find_str})'''):
    # print(f'''{innerrow.stb_num[:-1]}\t\t{innerrow.stb_num}\t\t{innerrow.cdsn_iuc}\t\t{innerrow.pcb_num}''')
    stb_found_dict[innerrow.stb_num.strip()[:-1]] = {
        "key_word": innerrow.stb_num.strip()[:-1],
        "stb_num": innerrow.stb_num,
        "cdsn_iuc": innerrow.cdsn_iuc,
        "pcb_num": innerrow.pcb_num
    }

# print(f'''keys: {stb_found_dict.keys()}''')
for stb_num_short in stb_found_dict.keys():
    try:
        pass  # print(f'''{stb_num_short}\t\t{stb_found_dict[stb_num_short]['stb_num']}\t\t{stb_found_dict[stb_num_short]['cdsn_iuc']}\t\t{stb_found_dict[stb_num_short]['pcb_num']}''')
    except KeyError:
        print(
            f'''{stb_num_short}\t{'NOT FOUND'}\t\t{'NOT FOUND'}\t\t{'NOT FOUND'}''')

print(f"\nTotal Entries: {len(stb_found_dict.keys())}")



# print(stb_found_dict.values())



out_df = pd.DataFrame(stb_found_dict.values())
out_df.to_excel(f'{pallet_col}.xlsx', index=False)
