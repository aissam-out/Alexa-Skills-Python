def evaluate_choices(alexas_choice, users_choice, data):
    """Given their answers, this function evaluates which one is the winner, alexa or the user."""
    
    if alexas_choice == data["PAPER"] and users_choice == data["SCISSORS"]:
        message = data["WINNER"].format(users_choice, alexas_choice)
        winner = "user"
    elif alexas_choice == data["PAPER"] and users_choice == data["ROCK"]:
        message = data["LOSER"].format(users_choice, alexas_choice)
        winner = "alexa"
    elif alexas_choice == data["SCISSORS"] and users_choice == data["PAPER"]:
        message = data["LOSER"].format(users_choice, alexas_choice)
        winner = "alexa"
    elif alexas_choice == data["SCISSORS"] and users_choice == data["ROCK"]:
        message = data["WINNER"].format(users_choice, alexas_choice)
        winner = "user"
    elif alexas_choice == data["ROCK"] and users_choice == data["PAPER"]:
        message = data["WINNER"].format(users_choice, alexas_choice)
        winner = "user"
    elif alexas_choice == data["ROCK"] and users_choice == data["SCISSORS"]:
        message = data["LOSER"].format(users_choice, alexas_choice)
        winner = "alexa"
    else:
        message = data["DRAW"].format(users_choice)
        winner = "draw"
    
    return winner, message
