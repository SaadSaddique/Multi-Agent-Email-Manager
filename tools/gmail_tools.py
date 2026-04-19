import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

def get_unread_emails(service, max_results=5):
    """List unread messages with basic metadata."""
    try:
        results = service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        detailed_messages = []
        for msg in messages:
            # Fetch minimal details for the sidebar
            m = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
            headers = m.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            detailed_messages.append({
                'id': msg['id'],
                'subject': subject,
                'sender': sender,
                'snippet': m.get('snippet')
            })
        return detailed_messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def _extract_body(payload):
    """Recursively extract the best available body text from a payload."""
    import re

    def decode_data(data):
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        return ""

    mime_type = payload.get('mimeType', '')
    parts = payload.get('parts', [])

    # If this part has sub-parts, search them
    if parts:
        plain_text = ""
        html_text = ""
        for part in parts:
            result = _extract_body(part)
            if result.get('plain'):
                plain_text = result['plain']
            if result.get('html'):
                html_text = result['html']
        return {'plain': plain_text, 'html': html_text}

    # Leaf node
    data = payload.get('body', {}).get('data', '')
    if mime_type == 'text/plain':
        return {'plain': decode_data(data), 'html': ''}
    elif mime_type == 'text/html':
        html = decode_data(data)
        # Strip HTML tags for a readable plain-text fallback
        plain = re.sub(r'<[^>]+>', ' ', html)
        plain = re.sub(r'\s+', ' ', plain).strip()
        return {'plain': '', 'html': plain}
    return {'plain': '', 'html': ''}


def get_email_content(service, msg_id):
    """Get the content of a specific email."""
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

        extracted = _extract_body(payload)
        # Prefer plain text; fall back to stripped HTML
        body = extracted.get('plain') or extracted.get('html') or message.get('snippet', '')

        return {
            'id': msg_id,
            'threadId': message.get('threadId'),
            'subject': subject,
            'sender': sender,
            'body': body,
            'snippet': message.get('snippet')
        }
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def create_draft(service, to, subject, body, thread_id=None):
    """Create a draft email."""
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body_dict = {'message': {'raw': raw_message}}
        
        if thread_id:
            body_dict['message']['threadId'] = thread_id
            
        draft = service.users().drafts().create(userId='me', body=body_dict).execute()
        return draft
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def send_message(service, to, subject, body, thread_id=None):
    """Send an email."""
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body_dict = {'raw': raw_message}
        
        if thread_id:
            body_dict['threadId'] = thread_id
            
        message = service.users().messages().send(userId='me', body=body_dict).execute()
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def mark_as_read(service, msg_id):
    """Remove UNREAD label from message."""
    try:
        service.users().messages().batchModify(
            userId='me',
            body={
                'ids': [msg_id],
                'removeLabelIds': ['UNREAD']
            }
        ).execute()
        return True
    except HttpError as error:
        print(f'An error occurred: {error}')
        return False
