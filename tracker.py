#!/usr/bin/env python3
"""
Frontend Mastery 90-Day Tracker & Daily Logger
Automatically updates README.md progress, checklists, tables, and daily logs.
"""

import os
import re
import sys
import subprocess
from datetime import datetime

README_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")

# ANSI Color codes
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header():
    print(f"\n{CYAN}{BOLD}{'='*50}{RESET}")
    print(f"{CYAN}{BOLD}  🚀 FRONTEND MASTERY — DAILY PROGRESS TRACKER{RESET}")
    print(f"{CYAN}{BOLD}{'='*50}{RESET}\n")

def read_readme():
    if not os.path.exists(README_FILE):
        print(f"Error: {README_FILE} not found!")
        sys.exit(1)
    with open(README_FILE, "r", encoding="utf-8") as f:
        return f.read()

def write_readme(content):
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def find_next_incomplete_day(content):
    # Search the daily progress table for the first ⬜
    pattern = r"\|\s*(\d{2})\s*\|([^|]+)\|\s*⬜\s*\|"
    match = re.search(pattern, content)
    if match:
        day_num = int(match.group(1))
        topic = match.group(2).strip()
        return day_num, topic
    return 1, "HTML Foundation"

def get_day_topic(content, day_num):
    day_str = f"{day_num:02d}"
    pattern = rf"\|\s*{day_str}\s*\|([^|]+)\|"
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()
    return f"Day {day_str}"

def update_day_checklist(content, day_num):
    """Marks checklist items for this specific day as completed [-] -> [-x]"""
    day_str = f"{day_num:02d}"
    
    # Patterns for day headers in README
    # e.g., 📅 Day 01 — ..., 📅 Day 15, 🏆 DAY 83–85, 🏆 DAY 90
    day_regex = re.compile(
        rf"(?:📅\s*Day\s*{day_str}\b|🏆\s*DAY\s*{day_str}\b|📅\s*Day\s*{day_num}\b)",
        re.IGNORECASE
    )
    
    match = day_regex.search(content)
    if not match:
        # Try finding grouped days like Day 76–77 or DAY 83–85
        grouped_regex = re.compile(
            rf"(?:📅\s*Day\s*\d+[-–]\d+|🏆\s*DAY\s*\d+[-–]\d+)",
            re.IGNORECASE
        )
        for g_match in grouped_regex.finditer(content):
            header = g_match.group(0)
            nums = [int(n) for n in re.findall(r"\d+", header)]
            if len(nums) == 2 and nums[0] <= day_num <= nums[1]:
                match = g_match
                break

    if not match:
        return content, 0

    start_pos = match.start()
    # Find next section divider or next day header
    next_section = re.search(r"\n---\n|\n📅\s*Day|\n🏆\s*DAY", content[match.end():])
    end_pos = match.end() + (next_section.start() if next_section else len(content) - match.end())

    day_chunk = content[start_pos:end_pos]
    updated_chunk, count = re.subn(r"- \[ \]", "- [x]", day_chunk)
    
    new_content = content[:start_pos] + updated_chunk + content[end_pos:]
    return new_content, count

def update_daily_table(content, day_num):
    day_str = f"{day_num:02d}"
    pattern = rf"(\|\s*{day_str}\s*\|[^|]+\|)\s*⬜\s*\|"
    new_content, count = re.subn(pattern, r"\g<1> ✅ |", content)
    return new_content

def update_progress_counter(content):
    # Count how many ✅ exist in the DAILY PROGRESS table
    table_match = re.search(r"📈 DAILY PROGRESS.*?(?=---|\Z)", content, re.DOTALL)
    if table_match:
        table_text = table_match.group(0)
        done_count = len(re.findall(r"\|\s*✅\s*\|", table_text))
    else:
        done_count = len(re.findall(r"\|\s*✅\s*\|", content))

    # Update Progress: "X / 90 Days"
    content = re.sub(
        r'Progress:\s*"[0-9]+\s*/\s*90\s*Days"',
        f'Progress: "{done_count} / 90 Days"',
        content
    )

    # Check phase completion
    # Phase 1: Days 1-20
    # Phase 2: Days 21-50
    # Phase 3: Days 51-75
    # Phase 4: Days 76-85
    def is_range_done(start_d, end_d):
        for d in range(start_d, end_d + 1):
            d_str = f"{d:02d}"
            if not re.search(rf"\|\s*{d_str}\s*\|[^|]+\|\s*✅\s*\|", content):
                return False
        return True

    if is_range_done(1, 20):
        content = content.replace("- [ ] Phase 1 — HTML & CSS", "- [x] Phase 1 — HTML & CSS")
    if is_range_done(21, 50):
        content = content.replace("- [ ] Phase 2 — JavaScript", "- [x] Phase 2 — JavaScript")
    if is_range_done(51, 75):
        content = content.replace("- [ ] Phase 3 — React", "- [x] Phase 3 — React")
    if is_range_done(76, 85):
        content = content.replace("- [ ] Phase 4 — Professional Frontend", "- [x] Phase 4 — Professional Frontend")
    if is_range_done(86, 86):
        content = content.replace("- [ ] Final Portfolio", "- [x] Final Portfolio")
    if is_range_done(90, 90):
        content = content.replace("- [ ] Final Project", "- [x] Final Project")

    return content, done_count

def append_learning_log(content, day_num, topic, learned, built, problem, solution, confidence, study_time, commit_info):
    day_str = f"Day {day_num:02d} — {topic}"
    today = datetime.now().strftime("%Y-%m-%d")

    entry = f"""
### 📅 {day_str} ({today})

- **📚 What I learned:** {learned}
- **💻 What I built:** {built}
- **🐛 Problems faced:** {problem if problem else 'None'}
- **✅ How solved:** {solution if solution else 'N/A'}
- **⭐ Confidence:** {confidence}/10
- **⏱️ Study Time:** {study_time} hours
- **🔗 Git / Notes:** {commit_info if commit_info else 'Completed'}

---
"""
    # Insert entry after "🧠 DAILY LEARNING LOG"
    marker = "🧠 DAILY LEARNING LOG"
    pos = content.find(marker)
    if pos != -1:
        # Find the line end of the marker or any following blank lines
        insert_pos = pos + len(marker)
        # Place it right under the heading
        content = content[:insert_pos] + "\n" + entry + content[insert_pos:]
    else:
        content += "\n" + entry

    return content

def run_git_operations(day_num, topic):
    try:
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print(f"{YELLOW}No git changes to commit.{RESET}")
            return

        print(f"\n{BLUE}Git status detected changes.{RESET}")
        commit_msg = f"docs(progress): complete Day {day_num:02d} — {topic}"
        
        do_git = input(f"{BOLD}Run git add, commit & push? (Y/n): {RESET}").strip().lower()
        if do_git in ("", "y", "yes"):
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            print(f"{GREEN}✓ Committed with message: \"{commit_msg}\"{RESET}")
            
            # Check if remote exists
            remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout.strip()
            if remotes:
                subprocess.run(["git", "push"], check=True)
                print(f"{GREEN}✓ Successfully pushed to GitHub!{RESET}")
            else:
                print(f"{YELLOW}No git remote configured. Skipped git push.{RESET}")
    except Exception as e:
        print(f"{YELLOW}Git operation note: {e}{RESET}")

def main():
    print_header()
    content = read_readme()

    next_day, suggested_topic = find_next_incomplete_day(content)
    
    # Prompt for Day Number
    day_input = input(f"Enter Day number (1–90) [{CYAN}Default: {next_day}{RESET}]: ").strip()
    if day_input:
        try:
            day_num = int(day_input)
        except ValueError:
            print("Invalid day number.")
            sys.exit(1)
    else:
        day_num = next_day

    topic = get_day_topic(content, day_num)
    print(f"\n{GREEN}Selected: Day {day_num:02d} — {topic}{RESET}\n")

    # 1. Update checklist items for this day
    mark_check = input(f"Mark all checklist items for Day {day_num:02d} as done [x]? (Y/n): ").strip().lower()
    if mark_check in ("", "y", "yes"):
        content, count = update_day_checklist(content, day_num)
        print(f"{GREEN}✓ Checked {count} task items for Day {day_num:02d}.{RESET}")

    # 2. Update Daily Table
    content = update_daily_table(content, day_num)
    print(f"{GREEN}✓ Marked Day {day_num:02d} as ✅ in the Daily Progress table.{RESET}")

    # 3. Update Progress Counter & Phases
    content, total_done = update_progress_counter(content)
    print(f"{GREEN}✓ Total Progress updated: {total_done} / 90 Days.{RESET}")

    # 4. Learning Log input
    print(f"\n{CYAN}{BOLD}--- Daily Learning Log ---{RESET}")
    learned = input("📚 What did you learn today?: ").strip() or topic
    built = input("💻 What did you build?: ").strip() or "Practice code & exercises"
    problem = input("🐛 Any problems faced? (press Enter to skip): ").strip()
    solution = input("✅ How did you solve it? (press Enter to skip): ").strip() if problem else ""
    confidence = input("⭐ Confidence rating (1-10) [Default: 8]: ").strip() or "8"
    study_time = input("⏱️ Study time in hours [Default: 2]: ").strip() or "2"
    commit_info = input("🔗 Git commit link or note [Optional]: ").strip()

    content = append_learning_log(
        content, day_num, topic, learned, built, problem, solution, confidence, study_time, commit_info
    )

    # Save to README.md
    write_readme(content)
    print(f"\n{GREEN}{BOLD}🎉 README.md successfully updated!{RESET}\n")

    # Git commit & push
    run_git_operations(day_num, topic)
    print(f"\n{CYAN}Keep up the great work! See you tomorrow for Day {day_num + 1:02d}! 🚀{RESET}\n")

if __name__ == "__main__":
    main()
