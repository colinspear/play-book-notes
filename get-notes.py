from __future__ import print_function
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/drive.readonly']


def start_service(service, version):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        serv = build(service, version, credentials=creds)
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
    finally:
        return serv


def get_doc(service, DOCUMENT_ID):
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    return document


def get_file_ids(service, folder_id):
    query = f"parents = '{folder_id}'"
    response = service.files().list(q=query).execute()
    file_ids = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = drive_service.files().list(q=query).execute()
        file_ids.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')

    file_ids = [f['id'] for f in file_ids]
    
    return file_ids


def get_notes(doc_service, document_id):
    doc = get_doc(doc_service, document_id)
    content = [doc['title']]
    for i in range(len(doc['body']['content'])):
        try:
            _ = doc['body']['content'][i]['paragraph']['elements'][0]['textRun']['content']
            _ = _.strip('\n')
            if _:  
                content.append(_)
        except KeyError:
            pass

        try:
            _ = doc['body']['content'][i]['table']['tableRows'][0]['tableCells'][0]['content'][1]['table']['tableRows'][0]['tableCells'][1]['content'][0]['paragraph']['elements'][0]['textRun']['content']
            _ = _.strip('\n')
            if _:  
                content.append(_)
        except (KeyError, IndexError):
            pass

    return content


def main():
    folder_id = '0B_FnnpWOvQutQ3ZZaFptTm83WUU'

    doc_service = start_service('docs', 'v1')
    drive_service = start_service('drive', 'v3')

    file_ids = get_file_ids(drive_service, folder_id)

    for file in file_ids:
        notes = get_notes(doc_service, file)
        text = "\n\n".join(notes)
        title = notes[0].split('"')[-2].strip('"')
        with open(f'notes/{title}.txt', 'w') as f:
            f.write(text)

if __name__ == '__main__':
    main()