import random

def randconds(start, end):
    if (start % 4) != 1:
        raise ValueError("Only start after increments of 4")
    if ((end-start) % 4) != 0:
        raise ValueError("Only generate conditions for ranges that are increments of 4")
    all_choices = ["Control","Margin","Robust_Gamma", "Robust_Performance"]
    current_choices = all_choices + []
    for i in range(end-start):
        if current_choices == []:
            current_choices = all_choices + []
        my_choice = random.choice(current_choices) 
        current_choices.remove(my_choice)
        print(i+start, "\t", my_choice)

if __name__ == "__main__":
    randconds(9,45)