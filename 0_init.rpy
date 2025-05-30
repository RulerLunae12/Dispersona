default persistent.human_dict = {}
default current_edit_word = None
default translation_text = ""
default translation_input = ""
default current_input_word = ""
default word_to_translate = ""
default temp_translation = ""
default edited_words = {}
default selected_word = None

init python:

    if not hasattr(persistent, "human_dict"):
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
    call screen human_dictionary()
    $ _window_show()
    return

label show_translation_screen(word):
    $ temp_translation = str(get_translation(word) or "")
    call screen enter_translation_screen(word)
    return

label dev_cleanup:
    $ clean_unused_words()
    return
