label enter_translation(word):
    $ translation_text = get_translation(word)["translation"]
    call screen enter_translation_screen(word, translation_text)
    return

init python:

    def normalize_word(word):
        return word.strip().lower()

    import re
    import os
    from renpy.text.text import Text  # Важно! Не забудь это

    def get_translation(word):
        word = normalize_word(word)
        entry = persistent.human_dict.get(word, "")
        if isinstance(entry, dict):
            return {
                "translation": entry.get("translation", ""),
                "known": entry.get("known", False)
            }
    # На случай строки (старый формат)
        elif isinstance(entry, str):
            return {
                "translation": entry,
                "known": True
            }
        return {
            "translation": "",
            "known": False
        }

    def set_translation(word, translation):
        word = normalize_word(word)
        if word not in persistent.human_dict:
            persistent.human_dict[word] = {"translation": "", "known": False}
        persistent.human_dict[word]["translation"] = translation
        persistent.human_dict[word]["known"] = True
        renpy.save_persistent()

    def show_enter_translation(word):
        renpy.call_screen("enter_translation_screen", word=word)

    def translate_filter(text):
        def replacer(match):
            word = match.group(1)
            cleaned = normalize_word(word)
            entry = get_translation(cleaned)
            translation = entry.get("translation", "")
            known = entry.get("known", False)

            if known and translation:
                return "{size=-10}" + translation + "\n{/size}" + word
            else:
                return "{a=translate:" + cleaned + "}" + word + "{/a}"

        return re.sub(r"\{translate=(.*?)\}", replacer, text)

    config.hyperlink_handlers["translate"] = lambda word: renpy.call_in_new_context("show_translation_screen", word)

    def parse_translate_text(text):
        """
        Парсим текст с тегами {translate=слово} и возвращаем list из:
        [(слово, перевод), ...] и обычные части текста.
        Например:
        "Привіт, {translate=друг}!" -> [ "Привіт, ", ("друг", "перевод"), "!" ]
        """
        result = []
        pos = 0
        pattern = re.compile(r'\{translate=([^}]+)\}')
        for m in pattern.finditer(text):
            start, end = m.span()
            if start > pos:
                # добавляем обычный текст между тегами
                result.append(text[pos:start])
            word = m.group(1)
            norm_word = normalize_word(word)
            translation = get_translation(norm_word)
            result.append( (word, translation, norm_word) )
            pos = end
        if pos < len(text):
            result.append(text[pos:])
        return result


    def is_valid_translation(text):
        return text.strip() != ""

    def migrate_dictionary_format():
        """
        Конвертує старі рядкові значення в словники з ключами 'translation' і 'known'.
        """
        if not hasattr(persistent, "human_dict"):
            persistent.human_dict = {}

        for word, data in list(persistent.human_dict.items()):
            if isinstance(data, str):
                persistent.human_dict[word] = {
                    "translation": data,
                    "known": True
                }

    def clean_unused_words():
        """
        Видаляє з persistent.human_dict ті слова, які не використовуються в .rpy-файлах.
        """
        used_words = set()

        # Прохід по всіх .rpy-файлах
        for root, dirs, files in os.walk("game"):
            for file in files:
                if file.endswith(".rpy"):
                    with open(os.path.join(root, file), encoding="utf-8") as f:
                        content = f.read()

                        # Пошук {a=translate:...}
                        used_words.update(re.findall(r'{a=translate:(.*?)}', content))

        # Нормалізація знайдених слів
        used_words = {normalize_word(w) for w in used_words}

        # Видалення невикористаних
        all_words = set(persistent.human_dict.keys())
        unused_words = all_words - used_words

        for word in unused_words:
            del persistent.human_dict[word]

        renpy.save_persistent()
        renpy.notify(f"Видалено {len(unused_words)} неактивних слів.")

    def init_temp_edits():
        result = {}
        for word, data in persistent.human_dict.items():
            if isinstance(data, dict) and data.get("known"):
                result[word] = data.get("translation", "")
        return result
