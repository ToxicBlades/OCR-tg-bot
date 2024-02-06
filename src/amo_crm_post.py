import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Environment variables
SUBDOMAIN = os.getenv('AMOCRM_SUBDOMAIN')
CLIENT_ID = os.getenv('AMOCRM_CLIENT_ID')
CLIENT_SECRET = os.getenv('AMOCRM_CLIENT_SECRET')
REDIRECT_URI = os.getenv('AMOCRM_REDIRECT_URI')

ACCESS_TOKEN = os.getenv('AMOCRM_ACCESS_TOKEN')
REFRESH_TOKEN = os.getenv('AMOCRM_REFRESH_TOKEN')
# Initialize a requests session
session = requests.Session()

def get_headers(access_token):
    """Return headers for the request."""
    return {
        'Content-Type': 'application/json',
        'User-Agent': 'amoCRM-oAuth-client/1.0',
        'Authorization': f'Bearer {access_token}'
    }

def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token."""
    url = f'https://{SUBDOMAIN}.amocrm.ru/oauth2/access_token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'redirect_uri': REDIRECT_URI
    }
    response = session.post(url, json=data)
    if response.status_code == 200:
        tokens = response.json()
        os.environ['AMOCRM_ACCESS_TOKEN'] = tokens['access_token']
        os.environ['AMOCRM_REFRESH_TOKEN'] = tokens['refresh_token']
        return tokens
    else:
        print('Error refreshing token:', response.text)
        return None


def fetch_contacts(access_token, refresh_token, page=1, all_contacts=[]):
    """Fetch contacts from amoCRM."""
    if page == 1:
        all_contacts = []

    url = f'https://{SUBDOMAIN}.amocrm.ru/api/v4/contacts'
    headers = get_headers(access_token)
    params = {
        'limit': 10,
        'page': page,
    }

    response = session.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if '_embedded' in data and 'contacts' in data['_embedded']:
            all_contacts.extend(data['_embedded']['contacts'])
        if '_links' in data and 'next' in data['_links']:
            fetch_contacts(access_token, refresh_token, page + 1, all_contacts)
        return all_contacts
    elif response.status_code == 401:
        # Attempt to refresh token and retry
        new_tokens = refresh_access_token(refresh_token)
        if new_tokens:
            return fetch_contacts(new_tokens['access_token'], new_tokens['refresh_token'], page, all_contacts)
        else:
            print('Failed to refresh token and retrieve contacts')
            return None
    else:
        print(f'Failed to fetch contacts: {response.text}')
        return None


def create_deal_contact_company(data,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN):

    url = f'https://{SUBDOMAIN}.amocrm.ru/api/v4/leads/complex'
    headers = get_headers(access_token)

    params = {
    "name": f'Deal for {data["name"]}',
    "_embedded": {
        "contacts": [
            {
                "first_name": data["name"],
                "responsible_user_id": 9805834,
                "updated_by": 0,
                "custom_fields_values": [
                    {
                        "field_id": 8187,
                        "values": [
                            {
                                "value": data["description"],
                            }
                        ],
                    }, {
                "field_id": 8191,
                "values": [
                    {
                        "value": data["email"]
                    }
                ]
            },
            {
                "field_id": 8189,
                "values": [
                    {
                        "value": data["phone_number"]
                    }
                ]
            }
                ],
            }
        ],
        "companies": [
            {
                "name": data["company_name"],
                "custom_fields_values": [
                    {
                        "field_id": 8197,
                        "values": [
                            {
                                "value": data["address"],
                            }
                        ],
                    },
                ],
            }
        ]
    },
    "responsible_user_id": 9805834,
    "pipeline_id": 7213102,
}

    response = session.post(url, json=[params], headers=headers)
    if response.status_code == 200:
        print('Deal created successfully')
        print(response)
    elif response.status_code == 401:
        new_tokens = refresh_access_token(refresh_token)
        if new_tokens:
            create_deal_contact_company(new_tokens['access_token'], new_tokens['refresh_token'], data)
        else:
            print('Failed to refresh token and create a deal')
    else:
        print(f'Failed to create a deal: {response.text}')
# Example usage
# if __name__ == "__main__":
#     ACCESS_TOKEN = os.getenv('AMOCRM_ACCESS_TOKEN')
#     REFRESH_TOKEN = os.getenv('AMOCRM_REFRESH_TOKEN')

#     data = {
#         "name": "ZAFER PALABIYIK",
#         "email": "zafer.palabiyik@ozsofra.com.mt",
#         "phone_number": "+356 9987 4001",
#         "company_name": "Ozsofra Group",
#         "address": "Triq il-Korp tal-Pijunieri, Bugibba, Malta",
#         "description": "Managing Director"
#     }

#     print(data['address'])

#     create_deal_contact_company(ACCESS_TOKEN, REFRESH_TOKEN, data)



#     # contacts = fetch_contacts(ACCESS_TOKEN, REFRESH_TOKEN)
#     # if contacts is not None:
#     #     print(f'Fetched {len(contacts)} contacts')
#     # else:
#     #     print('No contacts fetched')
