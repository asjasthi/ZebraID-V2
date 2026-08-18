import argparse
import re
import secrets
from pathlib import Path

DEFAULT_DATA_FILE = Path(__file__).with_name("ZebraID_V2_Natural_Data.txt")

def numbered_value(line):
    match = re.match(r"^\d+\.\s+(.+)$", line.strip())
    return match.group(1).strip() if match else None

def read_data(data_file=DEFAULT_DATA_FILE):
    path = Path(data_file)
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Keep ZebraID_V2_Natural_Data.txt beside main.py."
        )

    headings = {
        "100 TEMPLATES":"templates",
        "100 FIRST NAMES":"names",
        "100 LOCATIONS":"locations",
        "100 CAREER PROFILES":"careers",
        "100 RELATIONSHIP DESCRIPTIONS":"relationships",
        "100 WEEKEND ACTIVITIES":"weekends",
        "100 PET DESCRIPTIONS":"pets",
        "100 HOBBIES":"hobbies",
        "100 FOOD PREFERENCES":"foods",
    }

    data = {name: [] for name in headings.values()}
    active = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if line in headings:
            active = headings[line]
            continue

        if not line or set(line) <= {"=", "-"}:
            continue

        if active:
            value = numbered_value(line)
            if value:
                data[active].append(value)

    for section, values in data.items():
        if len(values) != 100:
            raise ValueError(
                f"Expected exactly 100 entries in {section}, found {len(values)}."
            )

    return data

def article_job(job):
    article = "an" if job[0].lower() in "aeiou" else "a"
    return f"{article} {job}"

def generate_biography(data_file=DEFAULT_DATA_FILE):
    data = read_data(data_file)

    template = secrets.choice(data["templates"])
    name = secrets.choice(data["names"])
    location = secrets.choice(data["locations"])

    career = secrets.choice(data["careers"])
    job, education, reason = [part.strip() for part in career.split("|", 2)]

    relationship = secrets.choice(data["relationships"])
    weekend = secrets.choice(data["weekends"])
    pet = secrets.choice(data["pets"])
    hobby = secrets.choice(data["hobbies"])
    food = secrets.choice(data["foods"])

    result = template
    replacements = {
        "[FNAME]": name,
        "[LOCATION]": location,
        "[ARTICLE_JOB]": article_job(job),
        "[EDUCATION]": education,
        "[CAREER_REASON]": reason,
        "[CAREER_REASON_CAP]": reason[0].upper() + reason[1:],
        "[RELATIONSHIP]": relationship,
        "[WEEKEND]": weekend,
        "[PET]": pet,
        "[HOBBY]": hobby,
        "[FOOD]": food,
    }

    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result

def main():
    parser = argparse.ArgumentParser(
        description="Generate a natural first-person ZebraID V2 biography."
    )
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--data", default=str(DEFAULT_DATA_FILE))
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    for i in range(1, args.count + 1):
        if args.count > 1:
            print(f"--- V2 Biography {i} ---")
        print(generate_biography(args.data))
        if args.prompt:
            print()
            print(args.prompt)
        if args.count > 1 and i != args.count:
            print()

if __name__ == "__main__":
    main()
