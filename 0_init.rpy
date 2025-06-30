default persistent.human_dict = {}
default temp_translation = ""
default persistent.first_cleanup_done = False
define local_temp = ""
default persistent.first_playthrough_done = False
default dictionary_button = True
default dictionary_screen_open = False
default closing_dict = False
default persistent.dictionary_page = 0
default from_edit_screen = False
default save_page = 1

define homifont = "fonts/Homifont.ttf"

init python:

    if not hasattr(persistent, "dictionary_page"):
        persistent.dictionary_page = 0

    dictionary_button = False

    if persistent.human_dict is None or not isinstance(persistent.human_dict, dict):
        persistent.human_dict = {}

    config.say_menu_text_filter = None 

    fade_transition = Dissolve(0.35)

    config.overlay_screens.append("show_dictionary_button")

label show_dictionary:
    $ from_edit_screen = False
    $ _window_hide()
    $ init_temp_edits()
    call screen human_dictionary()
    $ from_edit_screen = False
    $ _window_show()
    return

label show_translation_screen:
    $ word = _hyperlink_word
    $ temp_translation = persistent.human_dict.get(word, {}).get("translation", "")
    $ _window_hide()
    call screen enter_translation_screen(word=word)
    $ _window_show()
    return
    
label dev_cleanup:
    $ clean_unused_words()
    return

label return_to_dictionary:
    with fade_transition
    call screen human_dictionary
    return


init python:
    
    def on_hyperlink_clicked(link):
        if link.startswith("translate:"):
            word = link[len("translate:"):]
            renpy.call_in_new_context("call_translation", word)

    config.hyperlink_callback = on_hyperlink_clicked
