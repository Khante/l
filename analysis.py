from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt

from phrases import REJECTION_PHRASES


def load_messages(cache_file: str = "rejection_messages_full.json") -> list[dict]:
    with open(cache_file, "r") as f:
        return json.load(f)


def count_phrases_in_messages(messages: list[dict]) -> dict[str, int]:
    phrase_counts: dict[str, int] = {}
    for phrase in REJECTION_PHRASES:
        count = 0
        for msg in messages:
            text = (msg.get("subject", "") + " " + msg.get("body", "")).lower()
            if phrase.lower() in text:
                count += 1
        phrase_counts[phrase] = count
    return phrase_counts


def print_section(title: str, *stats: tuple[str, Any]) -> None:
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print("=" * 60)
    for label, value in stats:
        print(f"{label}: {value}")
    print("-" * 60)


def create_bar_chart(
    labels: list[str],
    values: list[int],
    title: str,
    xlabel: str,
    ylabel: str,
    filename: str,
    color: str = "#3498db",
    horizontal: bool = False,
) -> None:
    fig, ax = plt.subplots(
        figsize=(12, 8) if horizontal else (12, 6),
    )

    if horizontal:
        ax.barh(labels, values, color=color)
        for i, (label, value) in enumerate(zip(labels, values)):
            ax.text(
                value + max(values) * 0.01,
                i,
                str(value),
                va="center",
                fontsize=10,
                fontweight="bold",
            )
        ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
        ax.grid(axis="x", alpha=0.3, linestyle="--")
    else:
        ax.bar(labels, values, color=color, width=0.8)
        for i, (label, value) in enumerate(zip(labels, values)):
            if value > 0:
                ax.text(
                    i,
                    value + max(values) * 0.01,
                    str(value),
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    fontweight="bold",
                )
        ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
        ax.grid(axis="y", alpha=0.3, linestyle="--")

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(filename, dpi=100, bbox_inches="tight")
    print(f"✅ Chart saved as '{filename}'")
    plt.close()


def analyze_phrases(messages: list[dict]) -> None:
    phrase_counts = count_phrases_in_messages(messages)
    sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
    total_count = len(messages)

    print_section(
        "REJECTION EMAIL PHRASE BREAKDOWN ",
        ("Total (individual counts)", sum(phrase_counts.values())),
        ("Total (unique emails)", total_count),
    )

    for phrase, count in sorted_phrases:
        print(f"{count:4d} | {phrase}")

    print("Generating phrase chart... 📊\n")

    phrases = [p for p, c in sorted_phrases]
    counts = [c for p, c in sorted_phrases]

    create_bar_chart(
        labels=phrases,
        values=counts,
        title=f"Rejection Email Phrases Breakdown\nTotal Unique Rejections: {total_count}",
        xlabel="Number of Emails",
        ylabel="",
        filename="phrases.png",
        color="#e74c3c",
        horizontal=True,
    )


def analyze_times(messages: list[dict]) -> None:
    hours = [
        datetime.fromisoformat(msg["date"]).hour for msg in messages if msg.get("date")
    ]
    hour_counts = Counter(hours)

    print_section(
        "REJECTION EMAIL TIME DISTRIBUTION 🕐",
        ("Total emails with timestamps", len(hours)),
    )

    print("Generating time chart... 📊\n")

    hours_list = list(range(24))
    hour_counts_list = [hour_counts.get(h, 0) for h in hours_list]
    hour_labels = [f"{h:02d}:00" for h in hours_list]

    create_bar_chart(
        labels=hour_labels,
        values=hour_counts_list,
        title="Rejection Emails by Time of Day",
        xlabel="Hour of Day",
        ylabel="Number of Rejections",
        filename="times.png",
        color="#3498db",
        horizontal=False,
    )

    print("\nStay strong! Every 'no' is one step closer to a 'yes'! 💪")


def extract_name_from_email(from_field: str) -> str | None:
    if "<" in from_field:
        # Extract email from inside <>
        email = from_field[from_field.index("<") + 1 : from_field.rindex(">")]
    else:
        # Use entire string as email
        email = from_field

    # Split on @ and get the part before it
    if "@" in email:
        return email.split("@")[0].lower()

    return None


def get_sender_name_counts(messages: list[dict]) -> dict[str, int]:
    sender_counts: dict[str, int] = Counter()
    for msg in messages:
        from_field = msg.get("from", "")
        sender_name = extract_name_from_email(from_field)
        if sender_name:
            sender_counts[sender_name] += 1
    return dict(sender_counts)


def analyze_sender_names(messages: list[dict]) -> None:
    sender_counts = get_sender_name_counts(messages)
    sorted_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)

    # Take top 5
    sorted_senders = sorted_senders[:5]

    print_section(
        "SENDER NAMES ANALYSIS 📧",
        ("Total unique sender names", len(sender_counts)),
    )

    for sender, count in sorted_senders:
        print(f"{count:4d} | {sender}")

    print("Generating sender names chart... 📊\n")

    senders = [s for s, c in sorted_senders]
    counts = [c for s, c in sorted_senders]

    create_bar_chart(
        labels=senders,
        values=counts,
        title="Top 5 Most Common Email Sender Names",
        xlabel="Number of Emails",
        ylabel="",
        filename="sender_names.png",
        color="#2ecc71",
        horizontal=True,
    )


def main() -> None:
    print("Loading messages from rejection_messages_full.json... 📂")
    messages = load_messages()
    print(f"✅ Loaded {len(messages)} messages!\n")

    analyze_phrases(messages)
    analyze_times(messages)
    analyze_sender_names(messages)


if __name__ == "__main__":
    main()
