# -*- coding: utf-8 -*-


def parse_commit_message(message):
    """Given the full commit message (summary, body), parse out relevant information.

    Mimiron generates commit messages, commits, and pushes changes tfvar changes to
    remote. These generated commit messages contain useful information such as the service
    that was bumped, the person that bumped, environment etc.

    Args:
        message (str): The full git commit message

    Returns:
        Optional[dict]: A dictionary of useful information, None otherwise

    """
    data = {}
    for line in message.split('\n'):
        if not line:
            continue

        key, _, value = line.partition(':')
        if key == 'committed-by':
            name, _, email = value.strip().partition('<')

            data['author_name'] = name.strip()
            data['author_email'] = email.rstrip('>') or None
    return data or None
