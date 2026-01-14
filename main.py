import pandas as pd

filename = "EntryList.csv"
filepath = f"./{filename}"

LastPass_dictionary = {
    "url": "http://sn",
    "username": None,
    "password": None,
    "extra": "",
    "name": None,
    "grouping": "csv_import",
    "fav": None,
    "totp": 0,
}

def main():
    original_df = pd.read_csv(filepath)

    # remove rows where ConnectionType equals 'Group/Folder'
    original_df = original_df[original_df['ConnectionType'] != 'Group/Folder']

    # create new empty DataFrame for the transformed data
    transformed_df = pd.DataFrame(columns=LastPass_dictionary.keys())

    for _, row in original_df.iterrows():
        # drop NaN values from the row
        woker_df = row.dropna()
        # copy the csv template header from LastPass_dictionary
        transformed_row = LastPass_dictionary.copy()

        # map the fields from the original DataFrame to the transformed DataFrame
        for key, value in woker_df.items():
            if key == 'ConnectionType':
                continue
            elif key in ['Name', 'Url', 'Group']:
                if key == 'Group':
                    # special handling for 'ZZ Old Customers' group
                    if 'ZZ Old Customers' in value:
                        transformed_row = LastPass_dictionary.copy()
                        # set grouping to ToBeRemoved for this specific group
                        transformed_row['grouping'] = "csv_import/ToBeRemoved"
                        break
                    else:
                        transformed_row['grouping'] = f"csv_import/{value}"
                else:
                    transformed_row[key.lower()] = value
            elif key in ['CredentialUserName', 'CredentialPassword']:
                transformed_row[key.replace('Credential', '').lower()] = value
            else:
                transformed_row['extra'] += (f"{key}: {value}\n")

        # handle entries without a URL
        if transformed_row['url'] == "http://sn":
            transformed_row['extra'] += f"Username: {transformed_row['username']}\n" \
                                        f"Password: {transformed_row['password']}\n"
            transformed_row['username'], transformed_row['password'] = None, None

        # append the transformed row to the transformed DataFrame
        transformed_df = pd.concat([transformed_df, pd.DataFrame([transformed_row])], ignore_index=True)

        # previous implementation
        """transformed_row = LastPass_dictionary.copy()
        transformed_row['name'] = row.get('Name')
        if pd.notna(row.get('Url')):
            transformed_row['url'] = row.get('Url')
            transformed_row['username'] = row.get('CredentialUserName')
            transformed_row['password'] = row.get('CredentialPassword')
            transformed_row['extra'] = (
                f"{row.get('Host')}\n"
                f"{row.get('WebUserName')}\n"
                f"{row.get('WebPassword')}\n"
                f"{row.get('OtherName1')}\n"
                f"{row.get('OtherValue1')}\n"
                f"{row.get('OtherName2')}\n"
                f"{row.get('OtherValue2')}\n"
                f"{row.get('OtherName3')}\n"
                f"{row.get('OtherValue3')}\n"
                f"{row.get('URL')}\n"
            )
        else:
            transformed_row['url'] = "http://sn"
            transformed_row['username'] = None
            transformed_row['password'] = None
            transformed_row['extra'] = (
                f"Hostname: {row.get('CredentialDomain')}\n"
                f"Username: {row.get('CredentialUserName')}\n"
                f"Password: {row.get('CredentialPassword')}\n"
                f"{row.get('Host')}\n"
                f"{row.get('WebUserName')}\n"
                f"{row.get('WebPassword')}\n"
                f"{row.get('OtherName1')}\n"
                f"{row.get('OtherValue1')}\n"
                f"{row.get('OtherName2')}\n"
                f"{row.get('OtherValue2')}\n"
                f"{row.get('OtherName3')}\n"
                f"{row.get('OtherValue3')}\n"
                f"{row.get('URL')}\n"
            )

        transformed_df = pd.concat([transformed_df, pd.DataFrame([transformed_row])], ignore_index=True)"""
    
    print(transformed_df.info())
    
    # save the transformed DataFrame to a new CSV file
    transformed_df.to_csv("LastPass_Import.csv", index=False)

if __name__ == "__main__":
    main()
