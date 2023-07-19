"""
Typing program for users to practice their typing skills with and potentially compete with others for the highest WPM

This program utilises a Tkinter GUI to have a visually stimulating typing experience. Various techniques were used
to achieve a fluid typing game, such as a class that generates random words and moves them down a Tkinter canvas.
The purpose of this program is to allow a range of different users to hone their typing skills, with different levels
for beginner, intermediate, and advanced typists. Allows for the storage of user scores and the lookup of their scores.
"""
from tkinter import *
import random
import time
import json

# GLOBAL VARIABLES
ROOT_WIDTH = 300
ROOT_HEIGHT = 300
CANVAS_WIDTH = 225
CANVAS_HEIGHT = 225
DEFAULT_TEXT_FILE = "defaulttext.txt"
MIN_WORDS = 10
DEFAULT_PADDING = 5
WORD_SPEED_INCREMENT = 1.0005
DIFFICULTY_DICT = {"easy": [0.6, 4], "medium": [0.9, 5], "hard": [1.75, float("inf")]}
EXPLOSION_SPEED = 3
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 15
SCORE_FILE_NAME = "score_dict.json"
DEFAULT_UPDATE_SPEED = 16
DEFAULT_Y_SPAWN = 10
SMALL_FONT_SIZE = 10
MEDIUM_FONT_SIZE = 12
LARGE_FONT_SIZE = 14


class Word:
    def __init__(self, master, y=DEFAULT_Y_SPAWN, inherit_velocity=True):  # code run when an instance is created
        self.active = True  # if the word is active / hasn't been typed or destroyed
        self.difficulty = DIFFICULTY_DICT[chosen_difficulty]
        if inherit_velocity:
            list_item = list(active_words.keys())[0]
            object_ref = active_words.get(list_item)
            self.velocity = object_ref.velocity
        else:
            self.velocity = self.difficulty[0]
        self.max_word_length = self.difficulty[1]

        self.text = self.random_word()  # select a random word from the words list

        self.master = master
        self.y = y

        # create an instance attributes for explosion lines
        self.explosion_line_1 = None
        self.explosion_line_2 = None
        self.explosion_line_3 = None
        self.explosion_line_4 = None
        self.explosion_lines = []

        self.x = self.gen_coord()
        self.word_object = self.master.create_text(self.x, self.y, text=self.text, font=("TkDefaultFont", font_size))

        active_words[self.text] = self  # adds the text and ref to object to dictionary

        self.move()  # initiate movement

    def random_word(self):
        """
        selects a random word from the word list and returns it
        contains a while function that continuously selects a random word until it satisfies the given parameters
        of being shorter or equal to max word length and not already displayed on the screen
        :return: generates_word: the randomly chosen word
        """
        generated_word = ""
        while len(generated_word) < 1 or len(generated_word) > self.max_word_length or generated_word in active_words:
            generated_word = random.choice(words_list)
        return generated_word

    def gen_coord(self):
        """
        finds coordinates in which no other word is currently in, as to avoid collisions between words
        :return: potential_coord; the x val to generate the word object at
        """
        potential_coord = random.randint(30, CANVAS_WIDTH-30)
        while len(self.master.find_overlapping(potential_coord-10, 30, potential_coord+10, 70)) != 0:
            potential_coord = random.randint(30, CANVAS_WIDTH-30)

        return potential_coord

    def move(self):  # move the word down the canvas
        """
        controls word movement and checks if it within borders
        if the word is active, move the word using the move() function down the screen. if the word is off the
        screen, end the game
        :return:
        """
        if self.active:
            self.master.move(self.word_object, 0, self.velocity)
            try:
                if self.master.coords(self.word_object)[1] > CANVAS_HEIGHT:
                    show_end_screen()
            except IndexError:
                pass

            self.velocity *= WORD_SPEED_INCREMENT  # increases velocity
            root.after(DEFAULT_UPDATE_SPEED, self.move)  # repeat

    def explode(self):
        """
        generates explosion lines around the word and then calls the move_explosion_line function
        :return:
        """
        x = self.master.coords(self.word_object)[0]
        y = self.master.coords(self.word_object)[1]

        self.explosion_line_1 = self.master.create_line(x+20, y-20, x+30, y-30)  # top right
        self.explosion_lines.append(self.explosion_line_1)
        self.move_explosion_line(0, [EXPLOSION_SPEED, -EXPLOSION_SPEED])
        self.explosion_line_2 = self.master.create_line(x-20, y-20, x-30, y-30)  # top left
        self.explosion_lines.append(self.explosion_line_2)
        self.move_explosion_line(1, [-EXPLOSION_SPEED, -EXPLOSION_SPEED])
        self.explosion_line_3 = self.master.create_line(x + 20, y + 20, x + 30, y + 30)  # bottom right
        self.explosion_lines.append(self.explosion_line_3)
        self.move_explosion_line(2, [EXPLOSION_SPEED, EXPLOSION_SPEED])
        self.explosion_line_4 = self.master.create_line(x - 20, y + 20, x - 30, y + 30)  # bottom left
        self.explosion_lines.append(self.explosion_line_4)
        self.move_explosion_line(3, [-EXPLOSION_SPEED, EXPLOSION_SPEED])

    def move_explosion_line(self, instance_number, direction):
        """
        every frame, move the given explosion line in the given direction
        :param instance_number: the line number to retrieve the proper line
        :param direction: a list that contains the x and y values for the move function
        :return:
        """
        pos_x = self.master.coords(self.explosion_lines[instance_number])[0]
        pos_y = self.master.coords(self.explosion_lines[instance_number])[1]

        if 0 < pos_x < CANVAS_WIDTH or 0 < pos_y < CANVAS_HEIGHT:  # if the explosion lines can still be seen
            self.master.move(self.explosion_lines[instance_number], direction[0], direction[1])

            root.after(DEFAULT_UPDATE_SPEED, lambda: self.move_explosion_line(instance_number, direction))
        else:  # if the explosion lines are out of bounds, delete for efficiency
            self.master.delete(self.explosion_lines[instance_number])

    def del_first(self):
        """
        removes the first character of the self.text string using the del method
        :return:
        """
        self.text = self.text[1:]
        self.master.itemconfig(self.word_object, text=self.text)

    def destroy(self):
        """
        sets state of object to false, halts movement function to save processing, removes word item from canvas
        :return:
        """
        self.active = False
        self.master.delete(self.word_object)


def callback(entry_text):
    """
    checks user's input against stored correct word, visual feedback provided, updates vars
    called every time user edits the entry field. retrieves input and checks it against reference word spelling
    every time the user edits the entry field, i.e. types a character, this function is called. it checks the user's
    input against the reference word's spelling using an if/else statement. if the user has typed the correct character,
    the function calls the reference objects .del_first function to remove the first letter, and clears the entry
    field. this also sets the word colour to green. else, the word is set to red and no letter is removed.
    :param entry_text:
    :return:
    """
    try:  # tries following code
        global letter_num, words_typed, accuracy_list
        active_word = list(active_words.keys())[0]  # sets the current active word as the first in the dictionary
        object_ref = active_words.get(active_word)  # stores the object name in a variable
        typed_chars = entry_text.get().strip()  # retrieves user's input
        if typed_chars != "":  # if the user has typed something
            if typed_chars[0] == active_word[letter_num]:  # if the user has typed the correct letter
                object_ref.del_first()
                game_canvas.itemconfig(object_ref.word_object, fill="green")  # sets word colour to green
                letter_num += 1
                game_entry.delete(0, 'end')
                accuracy_list[0] += 1
            else:  # if the user enters the wrong character(s), set the word colour to red
                game_canvas.itemconfig(object_ref.word_object, fill="red")
                accuracy_list[1] += 1
            if letter_num == len(active_word):  # if the user has typed the whole word correctly
                object_ref.explode()
                game_canvas.delete(object_ref.word_object)
                del active_words[active_word]
                Word(game_canvas)
                letter_num = 0
                words_typed += 1
                next_word = active_words.get(list(active_words.keys())[0])
                game_canvas.itemconfig(next_word.word_object, fill="green")  # sets the next active word to green
    except IndexError:  # if there is an index error / nothing is in the active words list
        pass


def initiate_game():
    """
    called when game is started. focuses on entry, spawns the first 3 words, updated in_game to True, calls update_wpm()
    :return:
    """
    global start_time, in_game
    game_entry.focus()  # sets user focus to entry field so they do not need to manually click on it
    Word(game_canvas, DEFAULT_Y_SPAWN, False)
    first_word_ref = active_words.get(list(active_words.keys())[0])  # sets the first word spawned to green 
    game_canvas.itemconfig(first_word_ref.word_object, fill="green")
    Word(game_canvas, DEFAULT_Y_SPAWN-25)
    Word(game_canvas, DEFAULT_Y_SPAWN-40)
    start_time = time.time()
    in_game = True
    update_wpm()


def close():
    """
    closes the program by destroying root (main window)
    :return:
    """
    root.destroy()


def show_instructions():
    """
    hides the main menu and shows the instructions
    :return:
    """
    menu_frame.grid_remove()
    instruction_frame.grid()


def show_settings():
    """
    hides the main menu and shows the settings
    :return:
    """
    menu_frame.grid_remove()
    settings_frame.grid()


def show_score_screen():
    """
    hides the main menu and shows the score screen, clears the score info label in advance
    :return:
    """
    menu_frame.grid_remove()
    score_info_label.config(text="")
    score_frame.grid()


def prepare_game(text_file_name, difficulty):
    """
    import text file, hides the settings and shows the game frame
    :return:
    """
    global chosen_difficulty, words_list
    chosen_difficulty = difficulty  # updates difficulty

    error_label.grid_remove()  # hides the error message

    try:
        if text_file_name == "":  # if the user has not chosen to use their own file, use the default
            with open(DEFAULT_TEXT_FILE) as f:
                words_list = f.read().splitlines()
                settings_frame.grid_remove()
                game_frame.grid()
                initiate_game()
        else:  # if the user has chosen to use their own text file
            with open(text_file_name) as f:
                words_list = f.read().splitlines()
                for word in words_list:  # removes all characters after whitespace in every item in list
                    words_list[words_list.index(word)] = word.split(" ", 1)[0]
                non_duplicate_words_list = []
                for word in words_list:  # removes duplicate words
                    if word not in non_duplicate_words_list:
                        non_duplicate_words_list.append(word)
                words_less_than_min = 0
                for word in words_list:
                    if len(word) <= (DIFFICULTY_DICT[difficulty])[1]:
                        words_less_than_min += 1
                print(non_duplicate_words_list)
                if len(non_duplicate_words_list) >= MIN_WORDS and text_file_name.endswith('.txt') and \
                        words_less_than_min > 3:
                    settings_frame.grid_remove()
                    game_frame.grid()
                    initiate_game()
                else:  # creates a popup if the text file does not have enough words or incorrect file type
                    if text_file_name.endswith('.txt'):
                        popup = Toplevel(root)
                        few_words_label = Label(popup, text="your text file does not have enough words! please make "
                                                            "sure it has more than 10 non-duplicate words "
                                                            "OR make sure you have more than 5 short words as well "
                                                            "(less than 5 characters)")
                        few_words_label.pack()
                    else:
                        error_label.grid()
    except FileNotFoundError:  # if the file is not found show error label
        error_label.grid()


def back():
    """
    function to go back to menu by grid_removing frames and grid() menu frame
    :return:
    """
    instruction_frame.grid_remove()
    game_frame.grid_remove()
    end_frame.grid_remove()
    score_frame.grid_remove()
    menu_frame.grid()


def update_wpm():
    """
    updates the wpm variable
    if the number of words typed is greater than 0, retrieves current time, calculate time elapsed, calculates
    WPM after converting current time to minutes. calls function again if in_game is True, otherwise reset WPM item
    :return:
    """
    global wpm
    if words_typed > 0:  # if the user has correctly typed more than 0 words
        current_time = time.time()
        time_elapsed = current_time - start_time
        time_elapsed /= 60  # convert to minutes
        wpm = words_typed / time_elapsed  # find wpm
        wpm = int(round(wpm))  # rounds wpm to whole no.
        game_canvas.itemconfig(wpm_item, text="WPM: {}".format(wpm))
    if in_game:  # if the game is running, repeat the function
        root.after(DEFAULT_UPDATE_SPEED, update_wpm)
    else:
        game_canvas.itemconfig(wpm_item, text="WPM: ")  # resets the wpm_item


def update_timer():
    """
    called every 16 ms, updates the timer by subtracting the current time from the starting time
    :return: updated_time: time elapsed since game is started
    """
    updated_time = int(round(time.time() - start_time))
    game_canvas.itemconfig(timer_item, text="TIME: {}".format(updated_time))
    root.after(DEFAULT_UPDATE_SPEED, update_timer)
    return updated_time


def show_end_screen():
    """
    clears all game related variables and calculates user accuracy
    resets letter_num, start_time, words_typed, accuracy_list, sets in_game to False. updates end screen
    labels to respective values, changes to end_frame
    :return:
    """
    global letter_num, start_time, words_typed, in_game, accuracy_list
    time_seconds = update_timer()
    end_frame.focus()  # takes focus off of the entry field
    game_entry.delete(0, 'end')  # clears entry field
    for word in active_words:  # goes through active_words dictionary and deletes objects
        active_words[word].destroy()
    letter_num, start_time, words_typed = 0, 0, 0
    active_words.clear()  # clears active_words dict
    # switch to end_frame
    game_frame.grid_remove()
    end_frame.grid()
    try:  # try calculate user accuracy
        user_accuracy = accuracy_list[0]/(accuracy_list[0] + accuracy_list[1])
        user_accuracy = int(round(user_accuracy*100))
        accuracy_list = [0, 0]
    except ZeroDivisionError:  # except if the user has not typed anything
        user_accuracy = 0
    # updates scoring labels
    wpm_label.configure(text="WPM: {}".format(wpm))
    update_scores(wpm)  # updates the user's score in the main score file / dictionary
    accuracy_label.configure(text="ACCURACY: {}%".format(user_accuracy))
    timer_label.configure(text="TIME: {} seconds".format(time_seconds))


def name_checking():
    """
    check user's name
    get user name and store it as user_name, check to see if it satisfies requirements. if it does, send to menu, if
    not, create a popup alerting the user
    :return:
    """
    global user_name
    user_name = name_field.get().strip()
    # following if statement checks for spaces and character length
    if MIN_NAME_LENGTH <= len(user_name) <= MAX_NAME_LENGTH and user_name.find(" ") < 0:
        opening_frame.grid_remove()
        menu_frame.grid()
    else:  # create a popup if the user has not satisfied naming requirements
        popup = Toplevel(root)
        Label(popup, text="please revise your username (less than {} chars, more than {} chars, no spaces".format(
            MAX_NAME_LENGTH, MIN_NAME_LENGTH)).pack()


def update_scores(wpm_score):
    """
    updates the user's WPM score in the main score json file
    opens the score file, retrieves the dictionary from inside and stores it as score_dict. if the user's current score
    is higher than their top WPM, overwrite. then, re open the json file and update the dictionary inside
    :param wpm_score:
    :return:
    """
    with open(SCORE_FILE_NAME, 'r') as f:  # retrieve dictionary from json file
        score_dict = json.load(f)
    if user_name not in score_dict or score_dict[user_name] < wpm_score:
        score_dict[user_name] = wpm_score
    json_dict = json.dumps(score_dict)
    with open(SCORE_FILE_NAME, "w") as a:  # write the new data back to the json file
        a.write(json_dict)


def retrieve_score(requested_name):
    """
    find and display top score or retrieves the score of a given name
    opens SCORE_FILE_NAME, retrieves the dictionary from inside. sort through score dict and find top score holder and
    value. if the requested_name is empty, display this information. else, if the given name is in the keys of this
    dictionary, display the score through a label. If not, display error message through a label.
    :param requested_name: string containing the user's requested name to find score for
    :return:
    """
    with open(SCORE_FILE_NAME, "r") as f:  # opens score file
        score_dict = json.load(f)  # loads dict from file
        top_score_list = [0, ""]
        for name in score_dict:
            name_score = score_dict[name]
            if name_score > top_score_list[0]:
                top_score_list[0] = name_score
                top_score_list[1] = name
    if requested_name != "":
        if requested_name in score_dict:  # if the user's requested name is in the dict
            requested_score = score_dict[requested_name]
            score_info_label.config(text="{}'s top WPM is {}".format(requested_name, requested_score))
        else:  # if user's requested name is not in dict
            score_info_label.config(text="USER NOT FOUND")  # updates score_info_label with error message
    else:
        score_info_label.config(text="the highest score is held by {} with {}WPM".format(top_score_list[1],
                                                                                         top_score_list[0]))


def create_consent_popup():
    """
    creates a popup for the user to consent
    disables all children of opening_frame, creates a Toplevel with root as parent, creates label, configures label
    sets popup to top, making it on top of root
    :return:
    """
    for child in opening_frame.winfo_children():  # sets all children of opening_frame to disabled
        child.configure(state="disabled")
    consent_popup = Toplevel(root)
    consent_popup.geometry("300x300")
    consent_popup.resizable(width=False, height=False)
    consent_popup.configure(bg="grey13")
    consent_label = Label(consent_popup,
                          text="this program collects user data, such as usernames and scores. if you do "
                               "not wish to consent to this program storing this data and using it however "
                               "we want, please exit the program. else, please press the consent button "
                               "below. also, we are not liable for any leaked data. thanks")
    consent_label.config(font=("TkDefaultFont", 13), wraplength=250, bg="grey13", fg="red", anchor=N, justify=CENTER)
    consent_label.pack(padx=5, pady=5)
    consent_button = Button(consent_popup, text="CONSENT", command=lambda: consent(consent_popup))
    consent_button.pack(padx=5, pady=5)
    exit_consent_button = Button(consent_popup, text="quit if not consent", command=close)
    exit_consent_button.pack(padx=5, pady=5)
    consent_popup.attributes("-topmost", True)  # puts the popup above the main window


def consent(popup_name):
    """
    enables all children of opening_frame, destroys popup, places root on top
    :param popup_name: name of the consent popup
    :return:
    """
    for child in opening_frame.winfo_children():
        child.configure(state="normal")
    popup_name.destroy()
    root.attributes("-topmost", True)
    root.attributes("-topmost", False)  # prevents issue of root minimising upon consent


def update_font_size(size):
    global font_size
    if size == "small":
        font_size = SMALL_FONT_SIZE
    elif size == "medium":
        font_size = MEDIUM_FONT_SIZE
    elif size == "large":
        font_size = LARGE_FONT_SIZE


# variables
user_name = ""  # string for user name
active_words = {}  # list of words currently falling down
letter_num = 0
start_time = 0
words_typed = 0
in_game = False  # bool for whether or not the user is in game
wpm = 0
timer = 0
accuracy_list = [0, 0]
chosen_difficulty = ""  # string for chosen difficulty
words_list = []
font_size = MEDIUM_FONT_SIZE


# create widgets / root
root = Tk()
root.title("flynns typing game")
root.columnconfigure(0, weight=1)
root.configure(bg="grey43")
root.geometry("{}x{}".format(ROOT_WIDTH, ROOT_HEIGHT))
root.resizable(width=False, height=False)

# create frames

# main frames
opening_frame = Frame(root, bg="grey43")
menu_frame = Frame(root, bg="grey43")
instruction_frame = Frame(root, bg="grey43")
score_frame = Frame(root, bg="grey43")
game_frame = Frame(root, bg="grey43")
settings_frame = Frame(root, bg="grey43")
end_frame = Frame(root, bg="grey43")
# menu
top_frame = Frame(menu_frame, bg="grey63")
button_frame = Frame(menu_frame, bg="grey63")
image_frame = Frame(menu_frame, bg="grey63")

# grid frames

# main frames
opening_frame.grid(row=0, column=0)
menu_frame.grid(row=0, column=0)
instruction_frame.grid(row=0, column=0)
score_frame.grid(row=0, column=0)
game_frame.grid(row=0, column=0)
settings_frame.grid(row=0, column=0)
end_frame.grid(row=0, column=0)
# menu
top_frame.grid(row=0, column=0, sticky="WE", padx=10, pady=10)
top_frame.grid_columnconfigure(0, weight=1)
button_frame.grid(row=1, column=0, sticky="WE", padx=10, pady=10)
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=1)
image_frame.grid(row=2, column=0, padx=10, pady=10)
image_frame.grid_columnconfigure(0, weight=1)

# create widgets

# opening frame
info_label = Label(opening_frame, text="hi there, please enter your user name into the entry field below and then"
                                       "click continue. thanks")
# changes font size to make it larger
info_label.config(font=("TkDefaultFont", 17), wraplength=250, bg="grey43", anchor=N, justify=CENTER)
name_field = Entry(opening_frame)
continue_button = Button(opening_frame, text="CONTINUE", command=name_checking)
# menu
title_label = Label(top_frame, text="WELCOME TO FLYNN'S TYPING GAME")
start_button = Button(button_frame, text="START", command=show_settings)
instructions_button = Button(button_frame, text="INSTRUCTIONS", command=show_instructions)
scores_button = Button(button_frame, text="SCORES", command=lambda: [show_score_screen(), retrieve_score("")])
exit_button = Button(button_frame, text="EXIT", command=close)
type_writer_canvas = Canvas(image_frame, width=173, height=150, bg="grey63")
type_writer_canvas.grid(row=0, column=0, padx=10, pady=10)
type_writer_image = PhotoImage(file="typerwriter.png")
type_writer_canvas.create_image(0, 0, anchor=NW, image=type_writer_image)
# instructions
instructions_label = Label(instruction_frame, text="text falls from the sky. it is your job to type the words into the "
                                                   "entry field before they reach the bottom or you will die. you dont "
                                                   "have to press space after you type a word, but you can.")
# changes font size to make it larger
instructions_label.config(font=("TkDefaultFont", 17), wraplength=250, bg="grey43", anchor=N, justify=CENTER)
instructions_back_button = Button(instruction_frame, text="BACK", command=back)
# score frame
score_instructions_label = Label(score_frame, text="enter the name of the desired user below and then click the find "
                                                   "score button")
score_instructions_label.config(font=("TkDefaultFont", 13), wraplength=250, bg="grey43", fg="black", justify=CENTER)
retrieve_score_entry = Entry(score_frame)
retrieve_score_button = Button(score_frame, text="FIND SCORE", command=lambda: retrieve_score(retrieve_score_entry.get()
                                                                                              ))
score_back_button = Button(score_frame, text="BACK", command=back)
score_info_label = Label(score_frame, text="")
score_info_label.config(font=("TkDefaultFont", 17), wraplength=250, bg="grey43", anchor=N, justify=CENTER)
# settings
choose_text_label = Label(settings_frame, text="OPTIONAL : enter the name of your custom text file into the entry field"
                                               " below. make sure to include the .txt at the end!")
choose_text_label.config(font=("TkDefaultFont", 11), wraplength=250, bg="grey43", justify=CENTER)
custom_text = Entry(settings_frame)
small_size_button = Button(settings_frame, text="small font", command=lambda: update_font_size("small"))
medium_size_button = Button(settings_frame, text="medium font", command=lambda: update_font_size("medium"))
large_size_button = Button(settings_frame, text="large font", command=lambda: update_font_size("large"))
easy_button = Button(settings_frame, text="easy", command=lambda: prepare_game(custom_text.get(), "easy"))
medium_button = Button(settings_frame, text="medium", command=lambda: prepare_game(custom_text.get(), "medium"))
hard_button = Button(settings_frame, text="hard", command=lambda: prepare_game(custom_text.get(), "hard"))
error_label = Label(settings_frame, text="ERROR: invalid file name and/or type")
error_label.config(font=("TkDefaultFont", 13), wraplength=250, bg="grey43", fg="red", justify=CENTER)
# game
game_canvas = Canvas(game_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="grey73")
wpm_item = game_canvas.create_text(25, 15, text="WPM: ")
timer_item = game_canvas.create_text(25, 30, text="TIME: ")
sv = StringVar()
sv.trace("w", lambda name, index, mode, av=sv: callback(sv))  # trace method to run callback function when entry edited
game_entry = Entry(game_frame, textvariable=sv)
# end
wpm_label = Label(end_frame, text="")
wpm_label.config(font=("TkDefaultFont", 15), wraplength=250, bg="grey43", justify=CENTER)
accuracy_label = Label(end_frame, text="")
accuracy_label.config(font=("TkDefaultFont", 15), wraplength=250, bg="grey43", justify=CENTER)
timer_label = Label(end_frame, text="")
timer_label.config(font=("TkDefaultFont", 15), wraplength=250, bg="grey43", justify=CENTER)
end_back_button = Button(end_frame, text="BACK", command=back)

# grid widgets

# opening frame
info_label.grid(row=0, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
name_field.grid(row=1, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
continue_button.grid(row=2, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
# menu
title_label.grid(row=0, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
start_button.grid(row=0, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
scores_button.grid(row=0, column=1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
instructions_button.grid(row=0, column=2, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
exit_button.grid(row=0, column=3, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
# instructions
instructions_label.pack(padx=10, pady=10)
instructions_back_button.pack(pady=5)
# score frame
score_instructions_label.grid(row=0, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
retrieve_score_entry.grid(row=1, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
retrieve_score_button.grid(row=2, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
score_back_button.grid(row=3, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
score_info_label.grid(row=4, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
# settings
choose_text_label.grid(row=0, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, columnspan=3)
custom_text.grid(row=1, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, columnspan=3)
small_size_button.grid(row=2, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
medium_size_button.grid(row=2, column=1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
large_size_button.grid(row=2, column=2, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
easy_button.grid(row=3, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
medium_button.grid(row=3, column=1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
hard_button.grid(row=3, column=2, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
error_label.grid(row=4, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, columnspan=3)
error_label.grid_remove()  # hide the error label until an error with the file type or name occurs
# game
game_canvas.grid(row=0, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
game_entry.grid(row=1, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
# end
wpm_label.grid(row=0, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
accuracy_label.grid(row=0, column=1, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
timer_label.grid(row=1, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, columnspan=2)
end_back_button.grid(row=2, column=0, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, columnspan=2)

# hides all frames but main menu frame to start with
menu_frame.grid_remove()
game_frame.grid_remove()
instruction_frame.grid_remove()
score_frame.grid_remove()
settings_frame.grid_remove()
end_frame.grid_remove()

# runs starting functions
update_timer()
create_consent_popup()

# loops root
root.mainloop()
