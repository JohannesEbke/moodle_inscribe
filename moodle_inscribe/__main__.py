#!/usr/bin/env python3

import os

from argparse import ArgumentParser
from re import search
from typing import Dict, Optional, Tuple

from requests import get, post


def moodle_post(host, sesskey, data, moodle_session) -> Dict:
    response = post(
        'https://{host}/lib/ajax/service.php?sesskey={sesskey}&info=core_enrol_get_potential_users'.format(
            host=host, sesskey=sesskey
        ),
        json=data,
        cookies={'MoodleSession': moodle_session},
        headers={'Content-Type': 'application/json'}
    )
    if not response.ok:
        raise Exception(response.raw)
    json_response = response.json()
    if json_response[0].get('error'):
        raise Exception(json_response)
    return json_response[0]['data']


def get_enrolid_and_sesskey(host, course_id, moodle_session) -> Tuple[str, str]:
    html = get(
        'https://{host}/user/index.php?id={course_id}'.format(host=host, course_id=course_id),
        cookies={'MoodleSession': moodle_session}
    )
    html_str = html.content.decode()
    enrol_match = search('name="enrolid" value="([0-9]+)"', html_str)
    assert enrol_match
    enrolid = enrol_match.groups()[0]
    sesskey_match = search('name="sesskey" value="([^"]+)"', html_str)
    assert sesskey_match
    sesskey = sesskey_match.groups()[0]
    return enrolid, sesskey


def get_student(host, course_id, student_email, sesskey, enrol_id, moodle_session) -> Optional[Dict]:
    data = [{
        "index": 0,
        "methodname": "core_enrol_get_potential_users",
        "args": {
            "courseid": str(course_id),
            "enrolid": str(enrol_id),
            "search": str(student_email),
            "searchanywhere": True,
            "page": 0,
            "perpage": 101,
        },
    }]

    json_result = moodle_post(host, sesskey, data, moodle_session)

    if isinstance(json_result, dict):
        json_result = json_result['users']

    users = [user for user in json_result if user['email'] == student_email]
    if len(users) == 0:
        return None
    elif len(users) == 1:
        return users[0]
    else:
        raise Exception('"{}" not unique:\n{}'.format(student_email, users))


def inscribe_student(host, course_id, userid, sesskey, enrolid, moodle_session, role) -> None:
    get(
        'https://{host}/enrol/manual/ajax.php?'
        'mform_showmore_main=0&'
        'id={course_id}&'
        'action=enrol&'
        'enrolid={enrolid}&'
        'sesskey={sesskey}&'
        '_qf__enrol_manual_enrol_users_form=1&'
        'mform_showmore_id_main=0&'
        'userlist%5B%5D={userid}&'
        'roletoassign={role}&'
        'startdate=3&'
        'duration='.format(host=host, course_id=course_id, enrolid=enrolid, sesskey=sesskey, userid=userid, role=role),
        cookies={'MoodleSession': moodle_session}
    )


def read_emails(file) -> list:
    with open(file, 'r') as myfile:
        emails = myfile.read().split(os.linesep)
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
    parser.add_argument('--email', metavar='EMAIL', default=None, type=str, help='The email of the student to inscribe')
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
                inscribe_student(
                    args.host, args.course_id, student['id'], sesskey, enrolid, args.moodle_session, args.role
                )
                print('Successfully inscribed {}'.format(student['fullname']))
            else:
                inscribe_error = True
                print('No student found with email "{}", or student already inscribed.'.format(email))

    if inscribe_error:
        return 1
    return 0
