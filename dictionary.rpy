label enter_translation(word):
    $ print("📝 Вход в экран перевода для:", word)
    $ translation = get_translation(word)
    call screen enter_translation_screen(word=word, translation=translation)
    return

init python:

    import re
    import os
    from renpy.text.text import Text

    def normalize_word(word):
        if not word:
            renpy.log("[WARNING] normalize_word получил пустое или None слово")
            return ""
        return word.strip().lower()

    def get_translation(word):
        word = normalize_word(word)
        data = persistent.human_dict.get(word)
        if isinstance(data, dict):
            return data.get("translation", "")
        elif isinstance(data, str):
            return data
        return ""

    def set_translation(word, translation):
        word = normalize_word(word)
        if persistent.human_dict is None:
            persistent.human_dict = {}
        if word not in persistent.human_dict:
            persistent.human_dict[word] = {"translation": "", "known": True}
        persistent.human_dict[word]["translation"] = translation
        persistent.human_dict[word]["known"] = True
        renpy.save_persistent()


    def show_enter_translation(word):
        renpy.call_screen("enter_translation_screen", word=word)

    def translate_filter(text):
        def replacer(match):
            word = match.group(1)
            cleaned = normalize_word(word)
            translation = get_translation(cleaned)

            if translation:
                return "{size=-10}" + translation + "\n{/size}" + word
            else:
                return "{a=translate:" + cleaned + "}" + word + "{/a}"

        return re.sub(r"\{translate=(.*?)\}", replacer, text)

    config.hyperlink_handlers["translate"] = lambda word: renpy.call_in_new_context("show_translation_screen", word)

    def is_valid_translation(text):
        return text.strip() != ""

    def clean_unused_words():
        """
        Удаляет слова, которые не используются в .rpy-файлах.
        """
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
        renpy.notify(f"Удалено {len(unused_words)} неактивных слов.")

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
