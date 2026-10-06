from openai import OpenAI

from klartext.domain.models import Explanation, LetterResult

# Languages a caseworker can choose; codes follow BCP-47.
LANGUAGES = {
    "en": "English", "fr": "French", "de": "German", "it": "Italian", "tr": "Turkish",
    "ar": "Arabic", "uk": "Ukrainian", "ti": "Tigrinya", "prs": "Dari", "so": "Somali",
}

SYSTEM_PROMPT = """You explain official letters to people who do not understand the letter's language.

Rules:
- Write ONLY in {language}. Use short sentences and everyday words; at most 5 sentences.
- Use ONLY the facts listed by the user. Never add advice, legal knowledge or anything else.
- Keep names of institutions, amounts and dates exactly as given.
- Start with who sent the letter and what they want, then the deadline, then what happens if nothing is done."""


def facts_from(result: LetterResult) -> str:
    """List only the verified points of a result; unverified points never reach the explanation."""
    e = result.extraction
    lines = []
    if e.sender.verified:
        lines.append(f"Sender: {e.sender.value}")
    if e.deadline is not None and e.deadline.verified:
        when = e.deadline.value
    if e.deadline is not None and e.deadline.verified:
        when = e.deadline.value
        if result.days_left is not None:
            approx = "about " if result.days_left_estimated else ""
            when += f" ({approx}{result.days_left} days left)"
        lines.append(f"Deadline: {when}")
    lines += [f"Action: {a.value}" for a in e.actions if a.verified]
    lines += [f"If nothing is done: {c.value}" for c in e.consequences if c.verified]
    return "\n".join(lines)


def explain(client: OpenAI, model: str, result: LetterResult, language: str) -> Explanation:
    """Write a short plain-language explanation of the verified facts in the given language."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(language=LANGUAGES[language])},
            {"role": "user", "content": facts_from(result)},
        ],
        temperature=0,
    )
    return Explanation(language=language, text=(resp.choices[0].message.content or "").strip())