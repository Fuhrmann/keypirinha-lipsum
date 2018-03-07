import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import re
import json


class Lipsum(kp.Plugin):
    LABEL = "Lipsum"
    DESCRIPTION = "Generate lorem ipsum text"
    LOREM_IPSUM_API = "http://lipsum.com/feed/json"
    ITEMCAT = kp.ItemCategory.USER_BASE + 1

    # The default suggestions avaliable at the lipsum API
    SUGGESTION_PARAGRAPH = "paras"
    SUGGESTION_WORDS = "words"
    SUGGESTION_BYTES = "bytes"
    SUGGESTION_LISTS = "lists"

    def __init__(self):
        super().__init__()
        self._suggestions = {}

    def on_start(self):
        self._set_default_actions()
        self._initialize_suggestions()

    def on_catalog(self):
        self.set_catalog([
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=self.LABEL,
                short_desc=self.DESCRIPTION,
                target=self.LABEL,
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            )
        ])

    def on_suggest(self, user_input, items_chain):
        if items_chain:
            user_input = user_input.strip()
            ammount = str(self._search_number(user_input))

            suggestions = []
            for target, suggestion in self._suggestions.items():
                suggestions.append(self._create_default_suggestion(
                    ammount + " " + suggestion.label, "Generate " + suggestion.label, target))

            self.set_suggestions(
                suggestions, kp.Match.FUZZY, kp.Sort.LABEL_ASC)

    # Request the text and copy to the clipboard
    def on_execute(self, item, action):
        ammount = self._search_number(item.label())

        start = "yes"
        if action:
            start = action.name()

        text = self._fetch_text(item.target(), ammount, start)
        kpu.set_clipboard(text)
        self.info("Lorem Ipsum text copied to clipboard!")

    # Request the lispum API the text using the parameters
    def _fetch_text(self, type, ammount, start):
        try:
            opener = kpnet.build_urllib_opener()

            headers = []
            headers.append(('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'))
            opener.addheaders = headers[:]

            with opener.open(self.LOREM_IPSUM_API + "?amount=" + ammount + "&start=" + start + "&what=" + type) as request:
                response = request.read().decode(encoding="utf-8", errors="strict")

            data = json.loads(response)
            return data['feed']['lipsum']
        except:
            return "lipsum.com website could not be reached!"

    # Search for a number in a string
    def _search_number(self, text):
        paragraphs = re.search(r'\d+', text)
        if not paragraphs or paragraphs is None:
            paragraphs = 1
        else:
            paragraphs = paragraphs.group()

        return paragraphs

    # Just a wrapper to create a suggestion item
    def _create_default_suggestion(self, label, desc, target):
        return self.create_item(
            category=self.ITEMCAT,
            label=label,
            short_desc=desc,
            target=target,
            args_hint=kp.ItemArgsHint.FORBIDDEN,
            hit_hint=kp.ItemHitHint.IGNORE
        )

    def _initialize_suggestions(self):
        self._suggestions[self.SUGGESTION_PARAGRAPH] = Suggestion("paragraphs")
        self._suggestions[self.SUGGESTION_WORDS] = Suggestion("words")
        self._suggestions[self.SUGGESTION_LISTS] = Suggestion("lists")
        self._suggestions[self.SUGGESTION_BYTES] = Suggestion("bytes")

    def _set_default_actions(self):
        self.set_actions(self.ITEMCAT, [
            self.create_action(name="yes", label="Yes",
                               short_desc="Start with 'Lorem Ipsum...'"),
            self.create_action(name="no", label="No",
                               short_desc="Dont start with 'Lorem Ipsum...'")
        ])


class Suggestion():
    label = None

    def __init__(self, label):
        self.label = label
