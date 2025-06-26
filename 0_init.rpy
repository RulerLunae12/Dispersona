default persistent.human_dict = {}
default temp_translation = ""
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
    $ _window_hide()
    call screen enter_translation_screen(word=word)
    return
    
label dev_cleanup:
    $ clean_unused_words()
    return

init python:
    
    def on_hyperlink_clicked(link):
        if link.startswith("translate:"):
            word = link[len("translate:"):]
            renpy.call_in_new_context("call_translation", word)

    config.hyperlink_callback = on_hyperlink_clicked

    def show_dictionary_once():
        if not renpy.has_screen("human_dictionary"):
            renpy.call_in_new_context("show_dictionary")
