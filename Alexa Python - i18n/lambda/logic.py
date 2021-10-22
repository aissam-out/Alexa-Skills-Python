def evaluate_choices(alexas_choice, users_choice):
    """Given their answers, this function evaluates which one is the winner, alexa or the user."""
    
    if alexas_choice == "paper" and users_choice == "scissors":
        message = f"Congratulations! You won! You chose {users_choice}, while my choice was {alexas_choice}."
        winner = "user"
    elif alexas_choice == "paper" and users_choice == "rock":
        message = f"Loser! I won! You chose {users_choice}, while my choice was {alexas_choice}."
        winner = "alexa"
    elif alexas_choice == "scissors" and users_choice == "paper":
        message = f"Loser! I won! You chose {users_choice}, while my choice was {alexas_choice}."
        winner = "alexa"
    elif alexas_choice == "scissors" and users_choice == "rock":
        message = f"Congratulations! You won! You chose {users_choice}, while my choice was {alexas_choice}."
        winner = "user"
    elif alexas_choice == "rock" and users_choice == "paper":
        message = f"Congratulations! You won! You chose {users_choice}, while my choice was {alexas_choice}."
        winner = "user"
    elif alexas_choice == "rock" and users_choice == "scissors":
        message = f"Loser! I won! You chose {users_choice}, while my choice was {alexas_choice}."
        winner = "alexa"
    else:
        message = f"It's a draw! we both chose {users_choice}. It was nice to play with you."
        winner = "draw"
    
    return winner, message
