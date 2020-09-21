#!/usr/bin/env python3

import os

from argparse import ArgumentParser
from re import search
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

from requests import get, post


def moodle_post(host, data, moodle_session) -> Dict:
    response = post(
        'https://{}/enrol/manual/ajax.php'.format(host),
        data=urlencode(data),
        cookies={'MoodleSession': moodle_session},
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    )
    if not response.ok:
        raise Exception(response.raw)
    json_response = response.json()
    if json_response.get('error') or json_response.get('success') is not True:
        raise Exception(json_response)
    return json_response['response']


def get_enrolid_and_sesskey(host, course_id, moodle_session) -> Tuple[str, str]:
    html = get(
        'https://{host}/enrol/instances.php?id={course_id}'.format(host=host, course_id=course_id),
        cookies={'MoodleSession': moodle_session}
    )
    html_str = html.content.decode()
    enrol_match = search('https:\\/\\/{}\\/enrol\\/manual\\/manage.php\\?enrolid=([0-9]+)'.format(host), html_str)
    assert enrol_match
    enrolid = enrol_match.groups()[0]
    sesskey_match = search('"sesskey":"([^"]+)"', html_str)
    assert sesskey_match
    sesskey = sesskey_match.groups()[0]
    return enrolid, sesskey


def get_student(host, course_id, student_email, sesskey, enrolid, moodle_session) -> Optional[Dict]:
    data = {
        'id': course_id,
        'sesskey': sesskey,
        'action': 'searchusers',
        'search': student_email,
        'page': 0,
        'enrolcount': 0,
        'perpage': 25,
        'enrolid': enrolid
    }
    json_result = moodle_post(host, data, moodle_session)
    users = json_result['users']
    if len(users) == 0:
        return None
    elif len(users) == 1:
        return users[0]
    else:
        raise Exception('"{}" not unique:\n{}'.format(student_email, json_result))


def inscribe_student(host, course_id, userid, sesskey, enrolid, moodle_session, role) -> None:
    data = {
        'sesskey': sesskey,
        'id': course_id,
        'userid': userid,
        'enrolid': enrolid,
        'action': 'enrol',
        'role': role,
        'startdate': 3,
        'duration': 0,
        'recovergrades': 0,
    }
    moodle_post(host, data, moodle_session)

def read_emails(file) -> list:
    with open(file, 'r') as myfile:
        emails=myfile.read().split(os.linesep)
    return emails

def main() -> int:
    parser = ArgumentParser(description='Inscribe Students into a Moodle course by email')
    parser.add_argument('--host', metavar='HOST', type=str, help='The moodle host to run against', required=True)
    parser.add_argument(
        '--course-id',
        metavar='ID',
        type=int,
        help='The course id (look into the URL for the id parameter)',
        required=True
    )
    parser.add_argument(
        '--email', metavar='EMAIL', default=None, type=str, help='The email of the student to inscribe'
    )
    parser.add_argument(
        '--file',
        metavar='FILE',
        default=None,
        type=str,
        help='A file containing the email addresses of the students to inscribe separated by newlines'
    )
    parser.add_argument(
        '--moodle-session',
        metavar='SESSION',
        type=str,
        help='The Moodle Session to use (Copy from Developer Tools -> Storage -> Cookies -> "MoodleSession")',
        required=True
    )
    parser.add_argument(
        '--role',
        metavar='ROLE',
        type=int,
        default=5,
        help='The role to give the person to be inscribed. In my installation, 5 is for "participant"'
    )

    args = parser.parse_args()

    if not bool(args.email) ^ bool(args.file):
        parser.error('Please specify either --email or --file')

    emails = [args.email]
    if bool(args.file):
        emails = read_emails(args.file)


    inscribe_error = False
        
    for email in emails:
        email = email.strip()
        if len(email) != 0:
            enrolid, sesskey = get_enrolid_and_sesskey(args.host, args.course_id, args.moodle_session)
            student = get_student(args.host, args.course_id, email, sesskey, enrolid, args.moodle_session)
            if student:
                inscribe_student(args.host, args.course_id, student['id'], sesskey, enrolid, args.moodle_session, args.role)
                print('Successfully inscribed {}'.format(student['fullname']))
            else:
                inscribe_error = True
                print('No student found with email "{}", or student already inscribed.'.format(args.email))

    if inscribe_error:
        return 1
    return 0
