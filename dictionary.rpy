init -10 python:
    def translate_handler(word):
        print(f"[translate handler] Clicked on: {word}")
        renpy.call_in_new_context("call_translation", word)

    config.hyperlink_handlers["translate"] = translate_handler

label call_translation(word):
    call enter_translation_screen(word) from _call_enter_translation_screen
    return

label enter_translation_screen(word):
    $ value = persistent.human_dict.get(word, "")
    $ temp_translation = value.get("translation", "") if isinstance(value, dict) else value
    call screen enter_translation_screen(word=word)
    return

init python:

    def register_word(word):
        word = normalize_word(word)
        if word not in persistent.human_dict:
            persistent.human_dict[word] = ""

    def migrate_human_dict():
        if persistent.human_dict is None:
            persistent.human_dict = {}
        for word, val in list(persistent.human_dict.items()):
            if isinstance(val, str):
                persistent.human_dict[word] = {
                    "translation": val,
                    "known": bool(val.strip())
                }

    class SetDict(Action):
        def __init__(self, dict_obj, key, value):
            self.dict_obj = dict_obj
            self.key = key
            self.value = value

        def __call__(self):
            self.dict_obj[self.key] = self.value
            renpy.restart_interaction()

    import re
    import os
    from renpy.text.text import Text

    def normalize_word(word):
        if not word:
            return ""
        return word.strip().lower()

    def normalize_human_dict():
        if not isinstance(persistent.human_dict, dict):
            persistent.human_dict = {}

        for word, value in list(persistent.human_dict.items()):
            if isinstance(value, str):
                persistent.human_dict[word] = { "translation": value.strip() }

    def get_translation(word):
        word = normalize_word(word)
        register_word(word)

        data = persistent.human_dict.get(word)

        if isinstance(data, dict):
            return data.get("translation", "")
        elif isinstance(data, str):
            persistent.human_dict[word] = {
                "translation": data,
                "known": True
            }
            return data
        return ""

    def set_translation(word, translation):
        word = normalize_word(word)
        print(f"[set_translation] word: {word}, translation: {translation}")

        if not isinstance(persistent.human_dict, dict):
            print("[set_translation] human_dict is None или не dict — инициализируем")
            persistent.human_dict = {}

        persistent.human_dict[word] = {
            "translation": translation.strip(),
            "known": True
        }

        print(f"[set_translation] RESULT: {persistent.human_dict}")
        renpy.save_persistent()

    def show_enter_translation(word):
        word = normalize_word(word)
        translation = get_translation(word)
        renpy.call_screen("enter_translation_screen", word=word, translation=translation)

    def translate_filter(text):
        def tag_replacer(match):
            word = match.group(1)
            return process_word(word, word)

        def a_replacer(match):
            word = match.group(1)
            content = match.group(2)
            return process_word(word, content)

        def process_word(word_key, display_word):
            cleaned = normalize_word(word_key)

            if cleaned not in persistent.human_dict:
                persistent.human_dict[cleaned] = {"translation": "", "known": False}

            translation = get_translation(cleaned)

            result = "{a=translate:" + cleaned + "}"
            if translation:
                result += "{size=-10}" + translation + "\n{/size}"
            result += display_word + "{/a}"

            return result

        text = re.sub(r"\{translate=(.*?)\}", tag_replacer, text)

        text = re.sub(r"\{a=translate:(.*?)\}(.*?)\{/a\}", a_replacer, text)

        return text

    def is_valid_translation(text):
        return text.strip() != ""

    def set_translation_temp(word, temp_edits, value):
        temp_edits[word]["translation"] = value

    def clean_unused_words():    
        used_words = set()

        for root, dirs, files in os.walk("game"):
            for file in files:
                if file.endswith(".rpy"):
                    with open(os.path.join(root, file), encoding="utf-8") as f:
                        content = f.read()
                        used_words.update(re.findall(r'{a=translate:(.*?)}', content))

        used_words = {normalize_word(w) for w in used_words}

        all_words = set(persistent.human_dict.keys())
        unused_words = all_words - used_words

        for word in unused_words:
            del persistent.human_dict[word]

        renpy.save_persistent()

    def update_translations(temp_edits):
        for word, data in temp_edits.items():
            word = normalize_word(word)
            translation = data.get("translation", "").strip()
            if translation:
                persistent.human_dict[word] = {
                    "translation": translation,
                    "known": True
                }
        renpy.save_persistent()

    def init_temp_edits():
        global temp_edits
        temp_edits = {
            word: {"translation": data["translation"]}
            for word, data in persistent.human_dict.items()
            if isinstance(data, dict) and data.get("translation", "").strip() != ""
        }

label edit_translation(word):
    $ local_temp = ""
    call screen edit_translation_screen(word)
    if _return == "save":
        $ persistent.human_dict[word] = local_temp
        $ renpy.save_persistent()
    return
