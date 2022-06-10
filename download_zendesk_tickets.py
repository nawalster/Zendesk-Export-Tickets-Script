import requests
import os
import json
import datetime
import re
import errno

credentials = 'name@email.com/token', '**********'
session = requests.Session()
session.auth = credentials
zendesk = 'https://subdomain.zendesk.com'


def save(object, file):
    try:
        data = json.dumps(object, indent=4)
    except error:
        print(error)

    with open(file, "a") as f:
        f.write(data)


def check(fp):
    if os.path.exists(fp):
        return True
    return False


def mkdir(fp):
    try:
        os.makedirs(fp)
    except OSError as error:
        print(error)


def saveUser(user):
    cwd = os.getcwd()
    fp = os.path.join(cwd, 'data\\users\\')
    file = os.path.join(fp, str(user['id']) + '.json')
    if check(fp) == False:
        mkdir(fp)
    save(user, file)


def saveTicket(ticket):
    cwd = os.getcwd()
    fp = os.path.join(cwd, 'data\\tickets\\' + str(ticket['id']))
    file = os.path.join(fp, 'ticket.json')
    if check(fp) == False:
        mkdir(fp)

    save(ticket, file)

    getComments(ticket['id'])


def saveComment(comment, ticketId):
    cwd = os.getcwd()
    fp = os.path.join(cwd, 'data\\tickets\\' + str(ticketId) +
                      '\\comments\\' + str(comment['id']))
    file = os.path.join(fp, 'comment.json')
    if check(fp) == False:
        mkdir(fp)
    save(comment, file)

    getCommentFiles(comment, ticketId)


def download(uri, file):
    if check(file) == False:
        try:
            r = requests.get(uri)
        except requests.exceptions.RequestException as e:
            print(e)
            return

        try:
            with open(file, 'wb') as f:
                f.write(r.content)
        except Exception as error:
            print(error)
            print('***Important: error file path = ' + file)
            return


def getUsers():
    init_flag = True
    user_list = []

    url = zendesk + '/api/v2/users.json'

    while url:
        response = session.get(url)
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            continue
        if response.status_code != 200:
            print('UserList Error with status code {}'.format(response.status_code))
            return
        data = response.json()
        user_list.extend(data['users'])
        url = data['next_page']

        # Total count output
        if(init_flag == True):
            print("User Count: " + str(data['count']))
            init_flag = False

        # Each user name output
        for each_user in data['users']:
            saveUser(each_user)
            # print(" {}" + each_user['name'])


def getSearchTickets(from_date, to_date):
    init_flag = True
    ticket_list = []

    url = zendesk + '/api/v2/incremental/tickets.json?start_time=' + \
        str(datetime.datetime.strptime(from_date, "%Y-%m-%d").timestamp())

    total_ticket = 0
    while url:

        try:
            response = session.get(url)
            if response.status_code == 429:
                print('Rate limited! Please wait.')
                time.sleep(int(response.headers['retry-after']))
                continue
            if response.status_code != 200:
                print('TicketList Error with status code {}'.format(
                    response.status_code))
                print(url)
                return

            data = response.json()
            ticket_list.extend(data['tickets'])
            url = data['next_page']

            # Each ticket subject output
            for each_ticket in data['tickets']:
                if each_ticket['generated_timestamp'] > datetime.datetime.strptime(to_date, "%Y-%m-%d").timestamp():
                    print("Ticket Count: " + str(total_ticket))
                    exit()

                total_ticket = total_ticket + 1
                saveTicket(each_ticket)
                # print(" {}" + each_ticket['subject'])
        except Exception as error:
            print('***Important error:')
            print(error)
            exit()


def getComments(ticketID):
    init_flag = True
    comments_list = []

    url = zendesk + '/api/v2/tickets/' + str(ticketID) + '/comments.json'

    while url:
        response = session.get(url)
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            continue
        if response.status_code != 200:
            # print('Comment Error with status code {}'.format(response.status_code))
            print('Comment records do not exist')
            return

        data = response.json()
        comments_list.extend(data['comments'])
        url = data['next_page']

        # Total count output
        if(init_flag == True):
            print("Comment Count: " + str(data['count']))
            init_flag = False

        # Each comment name output
        for each_comment in data['comments']:
            each_comment['ticket_id'] = str(ticketID)
            saveComment(each_comment, ticketID)
            # print(" {}" + each_comment['body'])


def getCommentFiles(comment, ticketId):
    cwd = os.getcwd()

    if (len(comment['attachments']) > 0):
        for each_attach in comment['attachments']:
            uri = each_attach['content_url']

            fp = os.path.join(cwd, 'data\\tickets\\' + str(ticketId)+'\\comments\\' +
                              str(comment['id']) + '\\attachments\\' + str(each_attach['id']))

            fname_c = re.sub(r"[\"/:<>*|!?]", "", each_attach['file_name'])
            if len(fname_c) > 50:
                fname_c = fname_c[len(fname_c) - 50:]

            file = os.path.join(fp, fname_c)
            if check(fp) == False:
                mkdir(fp)

            download(uri, file)

    if(comment.get('data') is not None):
        comm_data = comment['data']
        if (comm_data.get('recording_url') is not None):
            uri = comm_data['recording_url']
            print("recording url: " + uri)

            fp = os.path.join(cwd, 'data\\tickets\\' + str(ticketId) +
                              '\\comments\\' + str(comment['id']) + '\\recordings')
            file = os.path.join(fp, str(comm_data['call_id'])+'.mp3')
            if check(fp) == False:
                mkdir(fp)

            download(uri, file)

# print('Downloading all users, this may take a few minutes.')
# getUsers()


from_date = input('Enter a start date in YYYY-MM-DD format: ')
try:
    datetime.datetime.strptime(from_date, '%Y-%m-%d')
except ValueError:
    raise ValueError("Incorrect data format, should be YYYY-MM-DD.")
    exit()

to_date = input('Enter an end date in YYYY-MM-DD format: ')
try:
    datetime.datetime.strptime(to_date, '%Y-%m-%d')
except ValueError:
    raise ValueError("Incorrect data format, should be YYYY-MM-DD.")
    exit()

print('Downloading search tickets between ' + from_date +
      ' and ' + to_date + ', this may take a few minutes.')
getSearchTickets(from_date, to_date)
