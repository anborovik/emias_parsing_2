import requests
import json
from datetime import datetime

from json_templates import get_specialists_info_json, get_doctor_info_json, get_doctor_schedule_json, create_appointment_json
from user_data import speciality_name, best_time, best_date

BASE_URL = 'https://emias.info/api/emc/appointment-eip/v1/'
ENDPOINTS = {
    'SPECIALISTS_INFO': '?getAvailableResourceScheduleInfo',
    'DOCTORS_INFO': '?getDoctorsInfo',
    'DOCTOR_SCHEDULE': '?getAvailableResourceScheduleInfo',
    'CREATE_APPOINTMENTS': '?createAppointment',
    'GET_APPOINTMENT': '?getAppointmentReceptionsByPatient'

}

def get_available_specialists(context):
    """
    Getting available doctors specialities
    """
    url = BASE_URL + ENDPOINTS['SPECIALISTS_INFO']
    response = requests.post(url, json=context)
    data = response.text
    json_response = json.loads(data)
    specialist_dict = {}
    for _ in json_response['result']:
        try:
            specialist_dict[_['name']] = [_['code'], _['onlyByRefferal']]
        except KeyError:
            specialist_dict[_['name']] = [_['code'], False]
    return specialist_dict

SPECIALITIES_DICT = get_available_specialists(get_specialists_info_json)

def get_doctors_info(context, speciality_name, specialities):
    """
    Getting doctor list for chosen speciality
    """
    context['params']['specialityId'] = specialities[speciality_name][0]
    if specialities[speciality_name][1] is True:
        context['params']['referralId'] = 121903232664  # def get_refferals_id()
    url = BASE_URL + ENDPOINTS['DOCTORS_INFO']
    response = requests.post(url, json=context)
    json_response = json.loads(response.text)
    doctors_dict = {}
    for _ in json_response['result']:
        doctors_dict[_['name']] = [
            _['arSpecialityId'],
            _['id'],
            _['complexResource'][0]['id']
            ]

    return doctors_dict


DOCTORS_DICT = get_doctors_info(get_doctor_info_json, speciality_name, SPECIALITIES_DICT)

def get_doctor_schedule(context, doctor_dict):
    """
    Getting schedule for doctors in doctor list
    """
    url = BASE_URL + ENDPOINTS['DOCTOR_SCHEDULE']
    schedule_dict = {}
    for name in doctor_dict.keys():
        ids = doctor_dict[name]
        context['params']['specialityId'] = ids[0]
        context['params']['availableResourceId'] = ids[1]
        context['params']['complexResourceId'] = ids[2]
        response = requests.post(url, json=context)
        json_response = json.loads(response.text)
        datetime_dict = {}
        for _ in json_response['result']['scheduleOfDay']:
            datetime_dict[_['date']] = [[datetime.fromisoformat(time['startTime']), datetime.fromisoformat(time['endTime'])] for time in _['scheduleBySlot'][0]['slot']]
        schedule_dict[name] = {
            'specialityId': ids[0],
            'availableResourceId': ids[1],
            'complexResourceId': ids[2],
            'receptionTypeId': json_response['result']['availableResource']['receptionType'][0]['code'],
            'schedule': datetime_dict,
            }
    return schedule_dict

SCHEDULE_DICT = get_doctor_schedule(get_doctor_schedule_json, DOCTORS_DICT)
print(SCHEDULE_DICT)

def create_appointment(context, schedule_dict, b):
    """
    Creating appointment by the best coincidence to nesessary date and time
    """
    best_date_iso = datetime.date.fromisoformat(best_date)
    best_time_iso = datetime.time.fromisoformat(best_time)

    pass

    
create_appointment(create_appointment_json, SCHEDULE_DICT, best_date, best_time)

