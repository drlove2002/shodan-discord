from urllib.request import urlopen


NORMALIZE_CHARS = {
    "Š": "S",
    "š": "s",
    "Ð": "Dj",
    "Ž": "Z",
    "ž": "z",
    "À": "A",
    "Á": "A",
    "Ã": "A",
    "Ä": "A",
    "Å": "A",
    "Æ": "A",
    "Ç": "C",
    "È": "E",
    "É": "E",
    "Ê": "E",
    "Ë": "E",
    "Ì": "I",
    "Í": "I",
    "Ï": "I",
    "Ñ": "N",
    "Ń": "N",
    "Ò": "O",
    "Ó": "O",
    "Ô": "O",
    "Õ": "O",
    "Ö": "O",
    "Ø": "O",
    "Ù": "U",
    "Ú": "U",
    "Û": "U",
    "Ü": "U",
    "Ý": "Y",
    "Þ": "B",
    "ß": "Ss",
    "à": "a",
    "á": "a",
    "ã": "a",
    "ä": "a",
    "å": "a",
    "æ": "a",
    "ç": "c",
    "è": "e",
    "é": "e",
    "ê": "e",
    "ë": "e",
    "ì": "i",
    "í": "i",
    "ï": "i",
    "ð": "o",
    "ñ": "n",
    "ń": "n",
    "ò": "o",
    "ó": "o",
    "ô": "o",
    "õ": "o",
    "ö": "o",
    "ø": "o",
    "ù": "u",
    "ú": "u",
    "û": "u",
    "ü": "u",
    "ý": "y",
    "þ": "b",
    "ÿ": "y",
    "ƒ": "f",
    "ă": "a",
    "î": "i",
    "â": "a",
    "ș": "s",
    "ț": "t",
    "Ă": "A",
    "Î": "I",
    "Â": "A",
    "Ș": "S",
    "Ț": "T",
}
ALPHABETS = (
    urlopen(
        "https://raw.githubusercontent.com/JEF1056/clean-discord/master/src/alphabets.txt"
    )
    .read()
    .decode("utf-8")
    .strip()
    .split("\n")
)
for alphabet in ALPHABETS[1:]:
    alphabet = alphabet
    for ind, char in enumerate(alphabet):
        try:
            NORMALIZE_CHARS[char] = ALPHABETS[0][ind]
        except KeyError:
            print(alphabet, len(alphabet), len(ALPHABETS[0]))
            break
NORMALIZE_CHARS = dict(NORMALIZE_CHARS)
