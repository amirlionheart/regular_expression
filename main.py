import csv
import re
from pprint import pprint

PHONE_PATTERN = re.compile(r"\+7\(\d+\)\d+\S\d+\S\d+(?: доб\.\d+)?")


def normalize_name(contact):
    """Split lastname/firstname/surname across dedicated fields."""
    full_name = " ".join(contact[:3]).split()
    normalized = (full_name + ["", "", ""])[:3]
    contact[:3] = normalized
    return contact


def normalize_phone(phone):
    ext_match = re.search(r"доб\.?\s*(\d+)", phone)
    ext = ext_match.group(1) if ext_match else ""
    phone_main = re.sub(r"доб\.?\s*\d+", "", phone)

    digits = re.sub(r"\D", "", phone_main)
    if len(digits) == 11 and digits[0] in {"7", "8"}:
        digits = digits[1:]

    if len(digits) != 10:
        return phone

    normalized = f"+7({digits[:3]}){digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
    if ext:
        normalized += f" доб.{ext}"
    return normalized if PHONE_PATTERN.fullmatch(normalized) else phone


def merge_contacts(rows):
    header = rows[0]
    merged = {}

    for raw_contact in rows[1:]:
        contact = normalize_name(raw_contact)
        contact[5] = normalize_phone(contact[5])

        key = (contact[0], contact[1])
        if key not in merged:
            merged[key] = contact
            continue

        current = merged[key]
        merged[key] = [new or old for old, new in zip(current, contact)]

    return [header] + list(merged.values())


def main():
    with open("phonebook_raw.csv", encoding="utf-8") as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)

    cleaned_contacts = merge_contacts(contacts_list)
    pprint(cleaned_contacts)

    with open("phonebook.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerows(cleaned_contacts)


if __name__ == "__main__":
    main()
