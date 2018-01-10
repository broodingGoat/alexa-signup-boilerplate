from flask import Flask, render_template
from flask_ask import (
    Ask,
    request as ask_request,
    session as ask_session,
    statement,
    question as ask_question
)
import requests
import json
import random
import inspect

app = Flask(__name__)
ask = Ask(app, "/")
app.config['ASK_VERIFY_REQUESTS'] = False
backendAPI = "http://184.72.97.31:7080"
grade_map = {"1st" : "gradefirst", "2nd" : "gradesecond"}


"""
session variables to maintain

child_id : id for child, associated with a registered skill id
signup_step: current step for sign up process
child_name: name for child

"""

def get_question(grade, index):
    print inspect.stack()[0][3]
    uri = backendAPI + "/getquestion"
    payload = {}
    payload["gradeinfo"] = grade
    payload["index"] = index
    payload = json.dumps(payload)
    headers = {'content-type': "application/json"}
    response = requests.request("POST", uri, data=payload, headers=headers)
    print response.text
    question_dic = response.json()
    return question_dic

def update_score(rollnumber,points):
    uri_update_score = backendAPI + '/updatescore'
    payload = {}
    payload['rollnumber'] = rollnumber
    payload['points'] = points
    payload = json.dumps(payload)
    headers = {'content-type': "application/json"}
    response = requests.request("POST", uri_update_score, data=payload, headers=headers)

    uri_get_score = backendAPI + '/getscore'
    payload = {}
    payload['rollnumber'] = rollnumber
    payload = json.dumps(payload)
    headers = {'content-type': "application/json"}
    response = requests.request("POST", uri_get_score, data=payload, headers=headers)
    return response.text

def get_user_name(rollnumber):
    print inspect.stack()[0][3]
    uri = backendAPI + "/getkid"
    payload = {}
    payload["rollnumber"] = rollnumber
    payload = json.dumps(payload)
    headers = {'content-type': "application/json"}
    response = requests.request("POST", uri, data=payload, headers=headers)
    print response.text
    if response.status_code == 200:

        child_name = response.json()['name']
        print child_name
        return child_name
    else:
        return ""

def validate_if_alexa_skill_id_registered(app_id):
    """
    checks if user exists based alexa application skill id
    queries an api to check if user is valid or not. returns true if exists, false otherwise
    for purpose of testing setting to false
    :param app_id: 
    :return: true/false
    
    """
    print inspect.stack()[0][3]
    uri = backendAPI + "/getkid"
    payload = {}
    payload["deviceid"] = app_id
    payload = json.dumps(payload)
    headers = {'content-type': "application/json"}
    response = requests.request("POST", uri, data=payload, headers=headers)
    if "empty" in response.json().keys():
        return False
    else:
        return True

def create_user(child_name,child_id,app_id):
    """
    calls an api to create user with child_name, child_id, skill_id
    :param child_name: 
    :param child_id: 
    :return: true if user created successfully
    """
    print inspect.stack()[0][3]
    uri = backendAPI + "/addkid"
    payload = {}
    payload["rollnumber"] = child_id
    payload["name"] = child_name
    payload["deviceid"] = app_id
    payload["score"] = "0"
    payload = json.dumps(payload)
    headers = {'content-type': "application/json"}
    response = requests.request("POST", uri, data=payload, headers=headers)
    print response.text
    if response.json()["deviceid"] == app_id:
        return True # set to true for testing & boilerplate
    else:
        return False

@ask.intent("SignUpGetId")
@ask.intent("SignUpGetName")
def sign_up():
    print inspect.stack()[0][3]
    if ask_session.attributes == {}:
        text = render_template('error')
        return statement(text)

    if "signup_get_name" in ask_session.attributes.values():
        child_name = ask_request.intent.slots.SignUpName.value
        ask_session.attributes["signup_step"] = "signup_get_id"
        ask_session.attributes["child_name"] = child_name
        text = render_template('sign_up_get_id',name=child_name)
        return ask_question(text)

    if "signup_get_id" in ask_session.attributes.values():
        child_id = ask_request.intent.slots.SignUpId.value
        child_name = ask_session.attributes["child_name"]
        app_id = ask_session.application['applicationId']
        if create_user(child_name,child_id,app_id):
            text = render_template('sign_up_success',name=child_name,id=child_id)
            return statement(text)
        else:
            text = render_template('error')
            return statement(text)

@ask.intent("GetRollNumber")
def get_id():
    print inspect.stack()[0][3]
    rollnumber = ask_request.intent.slots.RollNumber.value
    name = get_user_name(rollnumber)
    ask_session.attributes["child_id"] = rollnumber
    text = render_template('ask_existing_user_grade', name=name)
    return ask_question(text)

@ask.intent("Hello")
def start():
    print inspect.stack()[0][3]
    if validate_if_alexa_skill_id_registered(ask_session.application['applicationId']):
    # if true, user exists. Fetch role number
        text = render_template('ask_existing_user_id')
        return ask_question(text)
    else:
        text = render_template('sign_up_intro')
        ask_session.attributes["signup_step"] = "signup_get_name"
        return ask_question(text)

@ask.intent("GetGrade")
def get_grade():
    print inspect.stack()[0][3]
    grade = ask.request.intent.slots.Grade.value
    if grade is None:
        grade = "1st"
    child_id = ask_session.attributes["child_id"]
    print grade
    print grade_map.keys()
    if grade in grade_map.keys():
        ask_session.attributes["grade"] = grade_map[grade]
        ask_session.attributes["child_id"] = child_id
        text = render_template('lets_play')
        return ask_question(text)

    else:
        text = render_template("not_supported_grade")
        return statement(text)


@ask.intent("LetsPlay")
def lets_play():
    print inspect.stack()[0][3]
    child_id = ask_session.attributes["child_id"]
    grade = ask_session.attributes["grade"]
    index = random.choice([0,1])
    question_dic = get_question(grade, index)
    ask_session.attributes["child_id"] = child_id
    ask_session.attributes["grade"] = grade
    ask_session.attributes["points"] = question_dic["points"]
    ask_session.attributes["answer"] = question_dic["answer"]
    text = render_template('question',ques=question_dic["ques"],points=question_dic["points"])
    reprompt_text = render_template('question_help',ques_help=question_dic["help"])
    return ask_question(text).reprompt(reprompt_text)


@ask.intent("MyAnswer")
def my_answer():
    print inspect.stack()[0][3]
    child_id = ask_session.attributes["child_id"]
    grade = ask_session.attributes["grade"]
    answer = ask_session.attributes["answer"]
    points = ask_session.attributes["points"]
    user_answer = ask.request.intent.slots.Answer.value
    if user_answer == int(answer):
        score = update_score(child_id,points)
        text = render_template('correct_response',score=score)
    else:
        text = render_template('incorrect_response',answer=answer)
    ask_session.attributes["child_id"] = child_id
    ask_session.attributes["grade"] = grade
    return ask_question(text)
if __name__ == '__main__':
    app.run(debug=True)