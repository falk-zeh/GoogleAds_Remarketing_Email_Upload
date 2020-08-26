from oracle_config import config as o_config
import cx_Oracle
import pandas as pd
from googleads import adwords
import hashlib
import sys
from time import process_time


# The "adwords-api.yml" must be altered with your personal credentials beforehand.


print('--------------------------------------------------------')
print('Start: Uploading Excluding Customer List for Remarketing')
print('--------------------------------------------------------')


def get_customers_email():
    try:
        oracle_connection = cx_Oracle.connect(o_config.connection_string)
        df_ora = pd.read_sql("""
            select distinct * from customers
                            """, oracle_connection, parse_dates=True)

        print(f'Success: Data from Oracle received')

    except Exception as e:
        print(e)
        sys.exit()

    finally:
        oracle_connection.close()

    emails = df_ora['EMAIL'].values.tolist()
    emails = [x.encode('utf-8') for x in emails]

    return emails


def adEmailsList(client, emails, user_list_id):
    user_list_service = client.GetService('AdwordsUserListService', 'v201809')

    members = [{'hashedEmail': NormalizeAndSHA256(email)} for email in emails]

    mutate_members_operation = {
        'operand': {
            'userListId': user_list_id,
            'membersList': members
        },
        'operator': 'ADD'
    }

    response = user_list_service.mutateMembers([mutate_members_operation])

    if 'userLists' in response:
        for user_list in response['userLists']:
            print('%d users successfully added to list "%s" and ID "%d".'
                  % (len(emails), user_list['name'], user_list['id']))

    return response


def NormalizeAndSHA256(s):
    return hashlib.sha256(s.strip().lower()).hexdigest()


def main(emails, adwordsAudienceId=99999999999):
    if emails[0] == 'No data found.':
        sys.exit('No emails found.')
    else:
        print(f'Success: Emails found: {len(emails)}')

    adwords_client = adwords.AdWordsClient.LoadFromStorage('adwords-api.yml')

    adEmailsList(adwords_client, emails, adwordsAudienceId)


if __name__ == '__main__':

    try:
        time_start = process_time()
        emails = get_customers_email()
        main(emails)

    except Exception as e:
        print(e)
        sys.exit()

    finally:
        print('---------------------------------------------------------')
        print('Finish: Uploading Excluding Customer List for Remarketing')
        time_stop = process_time()
        print(f'Elapsed time in seconds: {(time_stop - time_start)}')
        print('---------------------------------------------------------')
        sys.exit()
