from collections import namedtuple
import configparser
import json
import csv
import requests
import datetime

datetime_object = datetime.date.today()


def process_guid_json(guid_json):
    '''Process the individual GUID entry
    '''
    computer = namedtuple('computer',['hostname', 'connector_guid', 'last_seen'])

    connector_guid = guid_json.get('connector_guid')
    hostname = guid_json.get('hostname')
    last_seen = guid_json.get('last_seen')

    return computer(hostname, connector_guid, last_seen)

def process_response_json(response_json):
    processed_computers = set()
    
    for entry in response_json['data']:
        computer = process_guid_json(entry)
        processed_computers.add(computer)

    return processed_computers

def format_container(container):
    ''' Processes the duplicate_computers container and formats the output based on hostname
        Returns a dictionary that can be saved to disk as JSON
    '''
    hosts = {}

    for host_tuple in sorted(container):
        hostname = host_tuple.hostname
        guid = host_tuple.guid
        last_seen = host_tuple.last_seen
        hosts.setdefault(hostname, {})
        hosts[hostname][last_seen] = guid
    return hosts


def write_data_to_csv(hostname, guid, last_seen):
    """Writes data to a csv depending on what type of report is specified
    """
    # log to update will either be pre or post guid deletion
    csv_file = 'computers_to_delete{}.csv'.format(datetime_object)

    # open file and set header
    with open(csv_file, 'w', newline = '') as csvFile:
        fieldnames = ['HOSTNAME','GUID','LAST_SEEN']
        writer = csv.DictWriter(csvFile, fieldnames = fieldnames)

        writer.writeheader()
        # Iterate through list of computers & write each row to csv
        writer.writerow({'HOSTNAME': hostname, 'GUID': guid, 'LAST_SEEN': last_seen})

def get(session, url):
    '''HTTP GET the URL and return the decoded JSON
    '''
    response = session.get(url)
    response_json = response.json()
    return response_json

def main():
    '''The main logic of the script
    '''
    client_id = input('Enter the client id: ')
    api_key = input('Enter the api_key: ')

    #computers = set()

    # Instantiate request session object
    amp_session = requests.session()
    amp_session.auth = (client_id, api_key)

    # URL to query AMP
    url = 'https://api.amp.cisco.com/v1/computers?hostname%5B%5D='

    file = "hostnames.txt"

    #hosts = {}

    with open(file, 'r') as hostnames:
        for computer in hostnames:
            computer = computer.strip()
            computer_url = url + computer

             # Query the API
            response_json = get(amp_session, computer_url)

            if ((response_json['metadata']['results']['total']) >= 1):
                comp_tuple = process_response_json(response_json)
                for tuple in comp_tuple:
                    hostname = tuple.hostname
                    guid = tuple.connector_guid
                    last_seen = tuple.last_seen
                    print('hostname: {} guid: {} last_seen: {}'.format(hostname, guid, last_seen))

    hostnames.close()

    #print(hosts)

if __name__ == "__main__":
    main()