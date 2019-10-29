def application(env, start_response, response_state):

    status = "200 OK"
    headers = [("Content-Type", "text/plain")]

    start_response(status, headers)

    return "Pong"