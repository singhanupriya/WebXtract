import requests
import json
import flask
from flask import request,jsonify
from auth import *

# My JOB is to listen all the messages received to the BOT ( EVERYTHING ) that hookbuster will throw

app = flask.Flask(__name__)
app.config["DEBUG"]

@app.route('/',methods=['POST'])
def post():
    posted_data = request.json
    print("Here's the RAW Data received from Attachments:")
    print("======================================================================================")
    print(posted_data)
    print("======================================================================================")
    print("data",posted_data['data'])
    print("======================================================================================")
    #return posted_data['data']['id']

    id=posted_data['data']['id']
    url = f"https://webexapis.com/v1/attachment/actions/{id}"

    headers = {
        'content-type': "application/json",
        'authorization': "Bearer ZWVlNjU0MjctZDZjYy00YWRiLWI3ZGQtMzI0NTRkODkxOWRmYzY2N2E4YTAtNzky_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f",
        'accept': "application/json"

    }

    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    result=response.json()

    #query field on card
    query_space=result['inputs']['query']

    #sr field on card
    sr_space=result['inputs']['sr']

    room=result['roomId']
    parent_msg=result['messageId']
    person_to=result['personId']

    print(result['inputs']['query'])
    print(result['inputs']['sr'])
    #print(result['inputs']['choice'])
    #print(result['type'])
    print(result['roomId'])
    print(result['messageId'])
    print(f'Hello  {sr_space} {query_space}')


    #Once the user enters the SR and query and clicks on submit, the bot will respond with the SR and query entered
    if(result['inputs']['query'] and result['inputs']['sr']):

        person_id = result['personId']
        url_person = f"https://webexapis.com/v1/people/{person_id}"
        response_person = requests.request("GET", url_person, headers=headers)
        result_person = response_person.json()
        person_name = result_person["displayName"]
        person_id=result_person["emails"][0]
        print("person_id",person_id)
        #x is the list name after split fn
        x=person_id.split('@')

        user_id=x[0]


        #choice
        choice = result['inputs']['choice']

        #the user selects the space only radiobutton, query to be sent only on the space as a reply.
        if(choice=="space_only"):

            url_post="https://webexapis.com/v1/messages"
            #payload_post=json.dumps({"roomId":result['roomId'],"parentId":result['messageId'],'text':f'Hello {person_name}. Thank you for using this card, here is your query regarding the SR {sr_space} {query_space}'})

            #the bot reply will be a new msg so we get a reply option
            payload_post = json.dumps({"roomId": result['roomId'],'text': f'Hello {person_name}. Thank you for using this card, here is your query regarding the SR {sr_space} {query_space}'})

            response_post=requests.request("POST", url_post, data=payload_post, headers=headers)
            print("SR posted status",response_post.status_code)


        #user chooses option 2: space n sr, the query is immediately posted in the space n sr, we need to wait for 5 days, send the complete
        #response thread to the user, if he says yes- forward thread to sr else nothing.
        elif(choice=="space_n_sr"):

            url_post = "https://webexapis.com/v1/messages"
            # payload_post=json.dumps({"roomId":result['roomId'],"parentId":result['messageId'],'text':f'Hello {person_name}. Thank you for using this card, here is your query regarding the SR {sr_space} {query_space}'})

            # the bot reply will be a new msg so we get a reply option
            payload_post = json.dumps({"roomId": result['roomId'],
                                       'text': f'Hello {person_name}. Thank you for using this card, here is your query regarding the SR {sr_space} {query_space}. The query has been sent to the SR.'})

            response_post = requests.request("POST", url_post, data=payload_post, headers=headers)
            print("SR posted status", response_post.status_code)

            print("SR_SPACE", sr_space, 'QUERY_SPACE', query_space)
            run_task('team_sr_forward', sr_space, query_space, user_id)

            '''
            Cron job section

            result_parent = response_post.json()
            parent_msg_id_thread = result_parent["id"]
            print("parent_msg_id", parent_msg_id_thread)

            url_thread = f"https://webexapis.com/v1/messages?roomId={room}&parentId={parent_msg_id_thread}"

            response_thread = requests.request("GET", url_thread, headers=headers)
            print("SR posted status", response_thread.status_code)
            result_forward = response_thread.json()

            l = []
            print(len(result['items']))
            for i in range(len(result_forward['items'])):
                l.append(result_forward['items'][i]['text'])
                print(result_forward['items'][i]['text'])
            
            #Send a direct msg
            
            person= result['personId']
            
            url_direct_msg = 'https://webexapis.com/v1/messages'
            payload_direct = json.dumps(
                {'toPersonId': person, 'text': f'You have received the following responses to your query to {query_space} {l}.\n In case, you want to forward it to the SR {sr_space}, please reply YES to this thread, else reply NO.'})
            response_direct = requests.request("POST", url_direct_msg, data=payload_direct, headers=headers)
            print("Forward status", response_direct.status_code)
            
            response_direct1=response_direct.json()
            direct_msg_id=response_direct1["id"]
            direct_room=response_direct["roomId"]
            
            url_direct = f"https://webexapis.com/v1/messages?roomId={direct_room}&parentId={direct_msg_id}"

            response_direct_reply = requests.request("GET", url_thread, headers=headers)
            response_reply1=response_direct_reply.json()
            
            #response_reply2 is yes or no
            
            response_reply2= response_reply1['items'][0]['text']
            if(response_reply2=="YES"):
                run_task('team_sr_forward', sr_space, l, user_id)
                url_direct_msg_reply = 'https://webexapis.com/v1/messages'
                payload_direct = json.dumps(
                {'toPersonId': person, 'text': f'The thread has been forwarded to the SR'})
                response_direct4 = requests.request("POST", url_direct_msg_reply, data=payload_direct, headers=headers)
                print("Forward status", response_direct.status_code)
            else:
                url_direct_msg_reply = 'https://webexapis.com/v1/messages'
                payload_direct = json.dumps(
                {'toPersonId': person, 'text': f'The thread has not been forwarded to the SR'})
                response_direct4 = requests.request("POST", url_direct_msg_reply, data=payload_direct, headers=headers)
                print("Forward status", response_direct.status_code)
        
            
            
            

            # print("SR_SPACE", sr_space, 'QUERY_SPACE', query_space)
            
            
            '''
        #user chooses option 3: forward thread to sr, this needs to forwarded in real time, maybe every hour reposne is forwarded to the sr, no yes/no option given to user.
        elif(choice=='thread_to_sr'):



            url_post = "https://webexapis.com/v1/messages"
            # payload_post=json.dumps({"roomId":result['roomId'],"parentId":result['messageId'],'text':f'Hello {person_name}. Thank you for using this card, here is your query regarding the SR {sr_space} {query_space}'})

            # the bot reply will be a new msg so we get a reply option
            payload_post = json.dumps({"roomId": result['roomId'],
                                       'text': f'Hello {person_name}. Thank you for using this card, here is your query regarding the SR {sr_space} {query_space}. \n PS: Please reply to this thread. The complete thread will be forwarded to the SR.'})

            response_post = requests.request("POST", url_post, data=payload_post, headers=headers)
            print("SR posted status", response_post.status_code)

            #to get the parent msg it, to track the reply

            result_parent=response_post.json()
            parent_msg_id_thread=result_parent["id"]
            print("parent_msg_id",parent_msg_id_thread)


            '''
            #######This needs to be in the cron job, obtain thread##########

            url_thread = f"https://webexapis.com/v1/messages?roomId={room}&parentId={parent_msg_id_thread}"


            response_thread = requests.request("GET", url_thread, headers=headers)
            print("SR posted status", response_thread.status_code)
            result_forward=response_thread.json()

            l = []
            print(len(result['items']))
            for i in range(len(result_forward['items'])):
                l.append(result_forward['items'][i]['text'])
                print( result_forward['items'][i]['text'])

            # print("SR_SPACE", sr_space, 'QUERY_SPACE', query_space)
            run_task('team_sr_forward', sr_space, l, user_id)

            ############Cron job section ends############
            '''







        msg_id = result['messageId']
        url_delete = f"https://webexapis.com/v1/messages/{msg_id}"
        response_delete_card = requests.request("DELETE", url_delete, headers=headers)
        print("Card deletion", response_delete_card.status_code)

    ##Once the user enters query for techzone and clicks on submit, the bot will respond with the query entered
    if (result['inputs']['query'] and (not result['inputs']['sr'])):

        # choice
        choice = result['inputs']['choice']

        person_id=result['personId']
        url_person=f"https://webexapis.com/v1/people/{person_id}"
        response_person=requests.request("GET", url_person, headers=headers)
        result_person = response_person.json()
        person_name=result_person["displayName"]


        #user selects space only, wait for 5 days for the reply thread, send direct msg to user whether they want to forward to mailer or not.
        if (choice == "space_only"):

            url_post = "https://webexapis.com/v1/messages"
            payload_post_tech = json.dumps({"roomId": result['roomId'],'text': f'Hello {person_name}. Thank you for using this card. Here is your query  {query_space}.'})
            response_post_tech = requests.request("POST", url_post, data=payload_post_tech, headers=headers)
            print("Techzone posted status",response_post_tech.status_code)


            '''
            result_parent = response_post.json()
            parent_msg_id_thread = result_parent["id"]
            print("parent_msg_id", parent_msg_id_thread)

            url_thread = f"https://webexapis.com/v1/messages?roomId={room}&parentId={parent_msg_id_thread}"

            response_thread = requests.request("GET", url_thread, headers=headers)
            print("SR posted status", response_thread.status_code)
            result_forward = response_thread.json()

            l = []
            print(len(result['items']))
            for i in range(len(result_forward['items'])):
                l.append(result_forward['items'][i]['text'])
                print(result_forward['items'][i]['text'])
            
            #Send a direct msg
            
            person= result['personId']
            
            url_direct_msg = 'https://webexapis.com/v1/messages'
            payload_direct = json.dumps(
                {'toPersonId': person, 'text': f'You have received the following responses to your query to {query_space} {l}.\n In case, you want to forward it to the SR {sr_space}, please reply YES to this thread, else reply NO.'})
            response_direct = requests.request("POST", url_direct_msg, data=payload_direct, headers=headers)
            print("Forward status", response_direct.status_code)
            
            response_direct1=response_direct.json()
            direct_msg_id=response_direct1["id"]
            direct_room=response_direct["roomId"]
            
            url_direct = f"https://webexapis.com/v1/messages?roomId={direct_room}&parentId={direct_msg_id}"

            response_direct_reply = requests.request("GET", url_thread, headers=headers)
            response_reply1=response_direct_reply.json()
            
            #response_reply2 is yes or no
            
            response_reply2= response_reply1['items'][0]['text']
            if(response_reply2=="YES"):
                
                ##mail code to be added##
                
                url_direct_msg_reply = 'https://webexapis.com/v1/messages'
                payload_direct = json.dumps(
                {'toPersonId': person, 'text': f'The thread has been forwarded to the SR'})
                response_direct4 = requests.request("POST", url_direct_msg_reply, data=payload_direct, headers=headers)
                print("Forward status", response_direct.status_code)
            else:
                url_direct_msg_reply = 'https://webexapis.com/v1/messages'
                payload_direct = json.dumps(
                {'toPersonId': person, 'text': f'The thread has not been forwarded to the SR'})
                response_direct4 = requests.request("POST", url_direct_msg_reply, data=payload_direct, headers=headers)
                print("Forward status", response_direct.status_code)
        
            
            
            

            # print("SR_SPACE", sr_space, 'QUERY_SPACE', query_space)
            
            '''

        #for techzone part, option 2 n 3 do not hold, promt user for option 1.
        else:
            url_post = "https://webexapis.com/v1/messages"
            payload_post_tech = json.dumps({"roomId": result['roomId'],
                                            'text': f'Hello {person_name}. Thank you for using this card. Here is your query  {query_space}. There is no SR, please use option: Post to Space.'})
            response_post_tech = requests.request("POST", url_post, data=payload_post_tech, headers=headers)
            print("Techzone posted status", response_post_tech.status_code)


        msg_id = result['messageId']
        url_delete = f"https://webexapis.com/v1/messages/{msg_id}"
        response_delete_card = requests.request("DELETE", url_delete, headers=headers)
        print("Card deletion", response_delete_card.status_code)


    #Once the user clicks on forward to SR/techzon, get list of all msgs for the card thread, card id as parent msg id
    # if(result['inputs']['choice']):
        #choice doesn't exist oustide
        # choice = result['inputs']['choice']
        # url_forward=f'https://webexapis.com/v1/messages?roomId={room}&parentId={parent_msg}'
        # response_forward = requests.request("GET", url_forward, headers=headers)
        # #print("Techzone posted status", response_post_tech.status_code)
        # result_forward = response_forward.json()
        # print(result)
        # l=[]
        # print(len(result['items']))
        # for i in range(len(result_forward['items'])):
        #     l.append(result_forward['items'][i]['text'])
        #     print( result_forward['items'][i]['text'])
        #
        # print("l",l)

        # if (choice == 'thread_to_sr'):
        #
        #     person_id = result['personId']
        #     url_person = f"https://webexapis.com/v1/people/{person_id}"
        #     response_person = requests.request("GET", url_person, headers=headers)
        #     result_person = response_person.json()
        #     person_name = result_person["displayName"]
        #     person_id = result_person["emails"][0]
        #     print("person_id", person_id)
        #     # x is the list name after split fn
        #     x = person_id.split('@')
        #
        #     user_id = x[0]
        #
        #     print("sr_space",sr_space,"query_space",query_space)
        #
        #     url_post = "https://webexapis.com/v1/messages"
        #     # payload_post=json.dumps({"roomId":result['roomId'],"parentId":result['messageId'],'text':f'Hello {person_name}. Thank you for using this card, here is your query regarding the SR {sr_space} {query_space}'})
        #
        #     # the bot reply will be a new msg so we get a reply option
        #     payload_post = json.dumps({"roomId": result['roomId'],
        #                                'text': f'Hello {person_name}. Thank you for using this card, here is your query regarding the SR {sr_space} {query_space}. You have selected the reply thread to be forwarded to the SR {sr_space}.'})
        #
        #     response_post = requests.request("POST", url_post, data=payload_post, headers=headers)
        #     result_thread=response_post.json()
        #     # Once a new msg is posted, we need the msg id to track its reply thread
        #     msg_id_parent=result_thread["id"]
        #     print("msg_id_parent",msg_id_parent)
        #     print("SR posted status", response_post.status_code)








            #to get sr from last element of the list

            # msg_id=result['messageId']
            # url_delete=f"https://webexapis.com/v1/messages/{msg_id}"
            # response_delete_card=requests.request("DELETE", url_delete, headers=headers)
            # print("Card deletion", response_delete_card.status_code)
            #
            # txt=l[-1]
            # x=txt.split('SR ')
            #
            # y=((x[1].split(' '))[0])
            # #y is the sr obtained
            # url_post = "https://webexapis.com/v1/messages"
            # payload_post_tech = json.dumps({"roomId": result['roomId'],'text': f'The following thread has been sent to the SR {y}.'})
            # response_post_tech = requests.request("POST", url_post, data=payload_post_tech, headers=headers)
            # print("Techzone posted status", response_post_tech.status_code)
            #
            # # Send a direct msg to individual informing these msgs will be sent to SR/TZ
            # url_direct_msg = 'https://webexapis.com/v1/messages'
            # payload_direct = json.dumps(
            #     {'toPersonId': person_to, 'text': f'You have selected the following msgs to be sent to {choice} {l}'})
            # response_direct = requests.request("POST", url_direct_msg, data=payload_direct, headers=headers)
            # print("Forward status", response_direct.status_code)



        #This is a segment to send a direct msg to the user if he selects space and sr
        # if(choice=='space_n_sr'):
        #
        #     msg_id = result['messageId']
        #     url_delete = f"https://webexapis.com/v1/messages/{msg_id}"
        #     response_delete_card = requests.request("DELETE", url_delete, headers=headers)
        #     print("Card deletion", response_delete_card.status_code)
        #
        #     #Send a direct msg to individual informing these msgs will be sent to SR/TZ
        #     url_direct_msg='https://webexapis.com/v1/messages'
        #     payload_direct = json.dumps({'toPersonId':person_to,'text':f'You have selected the following msgs to be sent to {choice} {l}'})
        #     response_direct = requests.request("POST", url_direct_msg, data=payload_direct, headers=headers)
        #     print("Forward status", response_direct.status_code)







    return "Data obtained"

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8081) # To run our server