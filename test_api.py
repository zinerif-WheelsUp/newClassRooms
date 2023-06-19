import pytest
import requests
import json
import random
import operator
from pycountry import countries

def create_payload(actionType):
    random_users = random.randint(1,10)
    payload = {}
    payload = {"actionType": actionType, "users" : get_users(random_users)}
    return payload

def get_users(number):
    values = range(number)
    array_users = []
    url_request = "https://randomuser.me/api"
    for i in values:
        api_response = requests.get(url_request)
        users_data = api_response.json()["results"]
        array_users.append(users_data[0])
    return array_users

def post_request(payload):
    url = 'https://census-toy.nceng.net/prod/toy-census'
    #Requirement silent on header data - Just setting minimal expected data to validate against.
    expected_headers = {}
    expected_headers["Content-Type"] = "application/json"
    expected_headers["Connection"] = "keep-alive"

    # Note: Because of the json parameter the header content type is auto added
    # no need to pass it to the post request
    resp = requests.post(url, json=payload)
    assert resp.status_code == 200
    headers = resp.headers
    assert resp.headers.get("Content-Type") == expected_headers["Content-Type"]
    assert resp.headers.get("Connection") == expected_headers["Connection"]
    return resp.json()
def get_password_complexity(password):
    value = 0
    for char in password:
        if not char.isalpha():
            value += 1
    return value
def get_expected_gender_response(request_payload):
    expected_gender_response = []
    new_list = []
    expected_response_male = {'name': 'male'}
    male_count = 0
    expected_response_female = {'name': 'female'}
    female_count = 0
    #print("PAYLOAD -> :", request_payload['users'])
    #print("LEN OF PAYLOAD -->: ",len(request_payload['users']))
    for i in range(0, len(request_payload["users"])):
        assert request_payload['users'][i]['gender'] in ['male', 'female']
        #print("PAYLOAD BEING PROCESSED -> : ", request_payload['users'][i])
        if request_payload['users'][i]['gender'] == 'male':
            male_count = male_count + 1
        else:
            female_count += 1
    expected_response_male['value'] = male_count
    expected_response_female['value'] = female_count
    if male_count !=0:
        expected_gender_response.append(expected_response_male)
    if female_count != 0:
        expected_gender_response.append(expected_response_female)
    # Sort list based on value from highest to lowest
    expected_gender_response.sort(key=operator.itemgetter('value'), reverse = True)
    print("EXPECTED RESPONSE - SORTED")
    print(expected_gender_response)
    return expected_gender_response

def get_expected_countByCountry_response(request_payload, countryCodes):
    expected_countByCountry_response = []
    res_list = []
    #print("USER DATA -> :", request_payload['users'])
    #print("LENGTH -->: ", len(request_payload['users']))
    for i in range(0, len(request_payload["users"])):
        resp_dat = { }
        value = 0
        assert request_payload['users'][i]['nat'] in countryCodes
        resp_dat = {'name': request_payload['users'][i]['nat'], "value": value}
        for j in range(0, len(request_payload["users"])):
            if request_payload['users'][i]['nat'] == request_payload['users'][j]['nat']:
                value +=1
        resp_dat['value'] = value
        res_list.append(resp_dat)
    # Remove any duplicates entries
    for n in range(len(res_list)):
        if res_list[n] not in res_list[n + 1:]:
            expected_countByCountry_response.append(res_list[n])
        # Sort list based on value from highest to lowest
        expected_countByCountry_response.sort(key=operator.itemgetter('value'), reverse=True)
    print("EXPECTED RESPONSE - SORTED")
    print(expected_countByCountry_response)
    return expected_countByCountry_response

def get_expected_countPwdComplexity_response(request_payload):
    resp_length = 0
    expected_countPwdComplexity_response = []
    #print("USER DATA -> :", request_payload['users'])
    #print("LENGTH -->: ", len(request_payload['users']))

    if 'top' in request_payload and request_payload['top'] != 0 :
        resp_length = request_payload['top']
       # print("TOP OPTION IS BEING PASSED ->: ", resp_length)
    else:
        resp_length = len(request_payload["users"])
       # print("TOP OPTION IS NOT BEING PASSED ->: ", resp_length)

    for i in range(0, len(request_payload["users"])):
        password = request_payload['users'][i]['login']['password']
        pwd_complexity = get_password_complexity(password)
        expected_countPwdComplexity_response.append({'name': password, 'value': pwd_complexity})

    # Sort list based on value from highest to lowest
    expected_countPwdComplexity_response.sort(key=operator.itemgetter('value'), reverse=True)
    print("EXPECTED RESPONSE - SORTED")
    print(expected_countPwdComplexity_response)
    return expected_countPwdComplexity_response
def get_country_code():
    # Get Alpha country list
    alpha_countrycode = []
    for i in countries:
        alpha_countrycode.append(i.alpha_2)
    return alpha_countrycode

def execute_request_withtopoption(actionType, top_option_values):
    is_subset = False
    expected_request_response = []
    country_codes = get_country_code()
    request_payload = create_payload(actionType)
    for i in range(0, len(top_option_values)):
        request_payload['top'] = top_option_values[i]
        if actionType == 'countByGender' :
            expected_request_response = get_expected_gender_response(request_payload)
        elif actionType == 'countPasswordComplexity' :
            expected_request_response = get_expected_countPwdComplexity_response(request_payload)
        elif actionType == 'countByCountry' :
            expected_request_response = get_expected_countByCountry_response(request_payload, country_codes)
        actual_request_response = post_request(request_payload)
        ##print("ACTUAL REQUEST RESPONSE FOR: ", actionType)
        print("PASSED TOP OPTION VALUE -> :", request_payload['top'])
        print("ACTUAL REQUEST RESPONSE -> :", actual_request_response)
        # Validate response
        if top_option_values[i] == 0 :
            assert len(actual_request_response) == len(expected_request_response)
            validate_response(expected_request_response, actual_request_response)
        else:
            assert len(actual_request_response) <= top_option_values[i]
            if (all(x in actual_request_response for x in expected_request_response)):
                is_subset = True
                assert is_subset
def validate_response(expected_response, actual_response):
    values_actual = []
    values_expected = []
    assert len(actual_response) == len(expected_response)
    for i in range(0,len(actual_response)):
        values_actual.append(actual_response[i]['value'])
        values_expected.append(expected_response[i]['value'])
    assert values_expected == values_actual

def test_countByGender():
    countByGender_payload = create_payload('CountByGender')
    # Create expected response based on passed payload
    expected_countByGender_response = get_expected_gender_response(countByGender_payload)
    countByGender_response = post_request(countByGender_payload)
    print("ACTUAL REQUEST RESPONSE: ")
    print(countByGender_response)
    assert expected_countByGender_response == countByGender_response
    #Use above assert so sorting errors are not masked.
    ##validate_response(expected_countByGender_response, countByGender_response)

def test_countByCountry():
    country_codes = get_country_code()
    countByCountry_payload = create_payload('CountByCountry')
    # Create expected response based on passed payload
    expected_countByCountry_response = get_expected_countByCountry_response(countByCountry_payload,country_codes)
    countByCountry_response = post_request(countByCountry_payload)
    print("ACTUAL REQUEST RESPONSE: ")
    print(countByCountry_response)
    assert expected_countByCountry_response == countByCountry_response
    # Use above insert instead - so sorting errors are not masked
    ##validate_response(expected_countByCountry_response, countByCountry_response)

def test_countPasswordComplexity():
    countPwdComplexity_payload = create_payload('CountPasswordComplexity')
    # Create expected response based on passed payload
    expected_countPwdComplexity_response = get_expected_countPwdComplexity_response(countPwdComplexity_payload)
    countPwdComplexity_response = post_request(countPwdComplexity_payload)
    print("ACTUAL REQUEST RESPONSE: ")
    print(countPwdComplexity_response)
    assert expected_countPwdComplexity_response == countPwdComplexity_response
    # Use above assert so sorting errors are not masked.
    ##validate_response(expected_countPwdComplexity_response, countPwdComplexity_response)

def test_countByGender_withTopOption():
    top_option_values = [0, 5]
    execute_request_withtopoption('countByGender', top_option_values)

def test_CountByCountry_withTopOptions():
    top_option_values = [0, 5]
    execute_request_withtopoption('countByCountry', top_option_values)

def test_CountPasswordComplexity_withTopOption():
    top_option_values = [0,5]
    execute_request_withtopoption('countPasswordComplexity', top_option_values)





