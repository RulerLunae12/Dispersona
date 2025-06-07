default persistent.human_dict = {}
default current_edit_word = None
default temp_translation = ""
default edited_words = {}
default selected_word = None
default persistent.first_cleanup_done = False

init python:

    if persistent.human_dict is None or not isinstance(persistent.human_dict, dict):
        persistent.human_dict = {}


    config.say_menu_text_filter = None 

    style.dict_close_button = Style(style.button)
    style.dict_close_button.size = 18
    style.dict_close_button.padding = (5, 10)
    style.dict_close_button.xminimum = 100
    style.dict_close_button.background = None

    style.dict_close_button_text = Style(style.button_text)
    style.dict_close_button_text.color = "#ff0088"
    style.dict_close_button_text.hover_color = "#888"

label show_dictionary:
    $ _window_hide()
    $ init_temp_edits()
    call screen human_dictionary()
    $ _window_show()
    return

label show_translation_screen(word):
    $ temp_translation = persistent.human_dict.get(word, {}).get("translation", "")
    call screen enter_translation_screen(word)
    return

label dev_cleanup:
    $ clean_unused_words()
    return
