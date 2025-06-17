default persistent.human_dict = {}
default temp_translation = ""
default edited_words = {}
default selected_word = None
default persistent.first_cleanup_done = False
define local_temp = ""
default persistent.first_playthrough_done = False
default dictionary_button = True

define homifont = "fonts/Homifont.ttf"

init python:

    dictionary_button = False

    if persistent.human_dict is None or not isinstance(persistent.human_dict, dict):
        persistent.human_dict = {}

    config.say_menu_text_filter = None 

    config.overlay_screens.append("show_dictionary_button")

label show_dictionary:
    $ _window_hide()
    $ init_temp_edits()
    call screen human_dictionary()
    $ _window_show()
    return

label show_translation_screen:
    $ word = _hyperlink_word
    $ temp_translation = persistent.human_dict.get(word, {}).get("translation", "")
    call screen enter_translation_screen(word=word)
    return
    
label dev_cleanup:
    $ clean_unused_words()
    return
