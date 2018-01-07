from flask import Flask, render_template
from flask_ask import (
    Ask,
    request as ask_request,
    session as ask_session,
    statement,
    question as ask_question
)

app = Flask(__name__)
ask = Ask(app, "/")
app.config['ASK_VERIFY_REQUESTS'] = False


"""
session variables to maintain

child_id : id for child, associated with a registered skill id
signup_step: current step for sign up process
child_name: name for child

"""

def validate_if_alexa_skill_id_registered(app_id):
    """
    checks if user exists based alexa application skill id
    queries an api to check if user is valid or not. returns true if exists, false otherwise
    for purpose of testing setting to false
    :param app_id: 
    :return: true/false
    """

    return False # set to false for testing & boilerplate

def create_user(child_name,child_id,app_id):
    """
    calls an api to create user with child_name, child_id, skill_id
    :param child_name: 
    :param child_id: 
    :return: true if user created successfully
    """

    return True # set to true for testing & boilerplate


@ask.intent("SignUpGetId")
@ask.intent("SignUpGetName")
def sign_up():
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



@ask.intent("Hello")
def start():
    if validate_if_alexa_skill_id_registered(ask_session.application['applicationId']):
    # if true, user exists. Fetch role number
        return ask_question("Welcome back. Whats your id")
    else:
        text = render_template('sign_up_intro')
        ask_session.attributes["signup_step"] = "signup_get_name"
        return ask_question(text)



if __name__ == '__main__':
    app.run(debug=True)