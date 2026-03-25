import os, sys
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
from datetime import datetime

# ── Load API key from .env file ───────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Strip hidden spaces/newlines
if GROQ_API_KEY:
    GROQ_API_KEY = GROQ_API_KEY.strip()

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found. Please add it to your .env file.")
    sys.exit(1)

# Debug check (optional, remove later)
print("Loaded key prefix:", GROQ_API_KEY[:8], "...")

client = Groq(api_key=GROQ_API_KEY)
console = Console()

# History file
HISTORY_FILE = ".assistant_history.json"
# Extended language support
LANGUAGE_EXTENSIONS = {
    'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'jsx': 'javascript', 'tsx': 'typescript',
    'html': 'html', 'css': 'css', 'scss': 'scss', 'java': 'java', 'kt': 'kotlin', 'scala': 'scala',
    'go': 'go', 'rs': 'rust', 'cpp': 'cpp', 'c': 'c', 'h': 'cpp', 'cs': 'csharp',
    'rb': 'ruby', 'php': 'php', 'pl': 'perl', 'lua': 'lua', 'swift': 'swift', 'dart': 'dart',
    'sh': 'bash', 'bash': 'bash', 'yaml': 'yaml', 'json': 'json', 'sql': 'sql',
    'r': 'r', 'jl': 'julia', 'ex': 'elixir', 'erl': 'erlang', 'hs': 'haskell', 'clj': 'clojure'
}

LANGUAGE_NAMES = {
    'python': 'Python', 'javascript': 'JavaScript', 'typescript': 'TypeScript',
    'java': 'Java', 'cpp': 'C++', 'c': 'C', 'csharp': 'C#', 'go': 'Go', 'rust': 'Rust',
    'ruby': 'Ruby', 'php': 'PHP', 'swift': 'Swift', 'kotlin': 'Kotlin', 'dart': 'Dart',
    'sql': 'SQL', 'bash': 'Shell', 'r': 'R', 'julia': 'Julia', 'elixir': 'Elixir',
    'haskell': 'Haskell', 'clojure': 'Clojure'
}

def load_history():
    """Load command history"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_to_history(mode, input_data, output_data):
    """Save command to history"""
    history = load_history()
    history.append({
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "input": input_data[:200] if len(input_data) > 200 else input_data,
        "output": output_data[:200] if len(output_data) > 200 else output_data
    })
    # Keep only last 50 entries
    history = history[-50:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def ask_groq(system_prompt, user_message, max_tokens=1000):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        temperature=0.3,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def detect_language(filepath):
    """Detect language from file extension"""
    ext = filepath.split('.')[-1].lower()
    return LANGUAGE_EXTENSIONS.get(ext, 'text')

# ─── MODE 1: DEEP CODE ANALYSIS ──────────────────────────────────────────────
def mode_explain(filepath, deep=False):
    """Deep code analysis with multiple perspectives - supports all languages."""
    if not os.path.exists(filepath):
        console.print(f"[red]File not found:[/] {filepath}")
        return

    with open(filepath) as f:
        code = f.read()

    detected_lang = detect_language(filepath)
    lang_name = LANGUAGE_NAMES.get(detected_lang, detected_lang.upper())

    console.print(f"\n[dim]Analyzing:[/] {filepath}")
    console.print(f"[dim]Language:[/] {lang_name} | [dim]Lines:[/] {len(code.splitlines())} | [dim]Characters:[/] {len(code)}\n")

    lang_context = f"This is {lang_name} code. "

    if deep:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            task1 = progress.add_task("[cyan]Understanding structure...", total=None)
            system_overview = f"""{lang_context}You are a senior architect analyzing code.
Provide a high-level overview:
1. Purpose (1-2 sentences, plain English)
2. Architecture/Structure (how components relate)
3. Tech stack/dependencies used
4. Entry points and main flow
5. Language-specific features utilized

Be clear and architectural."""
            overview = ask_groq(system_overview, f"Analyze this code:\n\n{code}", max_tokens=600)
            progress.remove_task(task1)

            task2 = progress.add_task("[cyan]Deep diving into logic...", total=None)
            system_deep = f"""{lang_context}You are an expert code reviewer doing a thorough analysis.
For each function/class/component:
1. What it does
2. How it works (step-by-step)
3. Input/output contracts
4. Edge cases handled (or missed)
5. Dependencies and side effects
6. Language-specific idioms and patterns

Be technical but clear."""
            deep_analysis = ask_groq(system_deep, f"Deep analysis:\n\n{code}", max_tokens=1200)
            progress.remove_task(task2)

            task3 = progress.add_task("[cyan]Identifying patterns...", total=None)
            system_patterns = f"""{lang_context}You are a software patterns expert.
Identify:
1. Design patterns used (MVC, Factory, Observer, etc.)
2. Coding patterns (DRY violations, coupling issues, etc.)
3. Language-specific patterns and best practices
4. Best practices followed
5. Anti-patterns or code smells
6. Suggested improvements (prioritized)

Be specific with line references if possible."""
            patterns = ask_groq(system_patterns, f"Find patterns:\n\n{code}", max_tokens=800)
            progress.remove_task(task3)

            task4 = progress.add_task("[cyan]Security & performance check...", total=None)
            system_security = f"""{lang_context}You are a security and performance expert.
Analyze for:
1. 🔒 Security issues (injection, XSS, secrets, auth, language-specific vulnerabilities)
2. ⚡ Performance bottlenecks (loops, queries, memory, language-specific optimizations)
3. 🐛 Potential bugs (race conditions, null refs, edge cases, type errors)
4. ⚠️ Risk level for each issue (Critical/High/Medium/Low)

Be specific and actionable."""
            security = ask_groq(system_security, f"Security & performance audit:\n\n{code}", max_tokens=1000)
            progress.remove_task(task4)

        console.print(Panel(Markdown(overview), title="[cyan]📋 Overview[/]", border_style="cyan"))
        console.print()
        console.print(Panel(Markdown(deep_analysis), title="[cyan]🔍 Deep Analysis[/]", border_style="blue"))
        console.print()
        console.print(Panel(Markdown(patterns), title="[cyan]🎯 Patterns & Best Practices[/]", border_style="yellow"))
        console.print()
        console.print(Panel(Markdown(security), title="[cyan]🔒 Security & Performance[/]", border_style="red"))

        save_to_history("explain_deep", filepath, overview + deep_analysis)

    else:
        system = f"""{lang_context}You are a patient senior developer explaining code to a junior trainee.
For the given code, explain:
1. What this file/function does overall (1-2 lines, plain English)
2. How it works step by step (simple language, no jargon)
3. Language-specific features or idioms used
4. Key things to remember or watch out for
5. Any patterns or techniques used worth learning

Be friendly, clear, and beginner-focused."""

        with console.status("[bold green]Understanding the code..."):
            result = ask_groq(system, f"Explain this code:\n\n{code}", max_tokens=1000)

        console.print(Panel(Markdown(result), title=f"[cyan]Explanation: {filepath}[/]", expand=False))

        console.print()
        if Confirm.ask("[yellow]Want a deeper analysis? (patterns, security, performance)[/]", default=False):
            mode_explain(filepath, deep=True)

        save_to_history("explain", filepath, result)

# ─── MODE 2: AI CODE GENERATION ──────────────────────────────────────────────
def mode_generate():
    """AI-powered code generation in any language."""
    console.print("[yellow]🚀 AI Code Generation Mode[/]\n")

    console.print("[dim]Select target language:[/]")
    languages = ["Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "Go", "Rust",
                "PHP", "Ruby", "Swift", "Kotlin", "Dart", "SQL", "Shell/Bash", "Other"]

    for i, lang in enumerate(languages, 1):
        console.print(f"  {i}. {lang}")

    lang_choice = Prompt.ask("\nLanguage number or name", default="1")
    try:
        lang_idx = int(lang_choice) - 1
        target_lang = languages[lang_idx] if 0 <= lang_idx < len(languages) else lang_choice
    except ValueError:
        target_lang = lang_choice

    console.print(f"\n[dim]Selected:[/] {target_lang}\n")

    gen_type = Prompt.ask(
        "What to generate",
        choices=["function", "class", "script", "algorithm", "api", "database", "component"],
        default="function"
    )

    description = Prompt.ask(f"\nDescribe your {gen_type}")

    style = Prompt.ask(
        "Code style",
        choices=["production", "tutorial", "prototype"],
        default="production"
    )

    include_tests = Confirm.ask("Include unit tests?", default=False)

    style_map = {
        "production": "production-ready with proper error handling, validation, and documentation",
        "tutorial": "well-commented and tutorial-style for learning",
        "prototype": "concise prototype focused on core functionality"
    }

    with console.status(f"[bold green]Generating {target_lang} code..."):
        system = f"""You are an expert software engineer who writes clean, efficient, and production-quality code.

Generate {style_map[style]} code in {target_lang} that:
1. Solves the user's requirements completely
2. Follows {target_lang} best practices and idioms
3. Includes proper error handling
4. Is well-structured and maintainable

Provide:
1. Complete working code
2. Brief explanation
3. Usage example
4. Key features
{"5. Unit tests" if include_tests else ""}"""

        result = ask_groq(system, f"Generate a {gen_type} in {target_lang}: {description}", max_tokens=2000)

    console.print(Panel(Markdown(result), title=f"[cyan]Generated {target_lang} Code[/]", expand=False))
    save_to_history("generate", description, result)

# ─── MODE 3: SMART DEBUGGING ─────────────────────────────────────────────────
def mode_debug():
    """Smart debugging assistant."""
    console.print("[yellow]🔧 Smart Debugging Mode[/]\n")

    console.print("What kind of issue?")
    console.print("  1. Error/Exception")
    console.print("  2. Bug/Unexpected behavior")
    console.print("  3. Performance issue")
    console.print("  4. Logic error")

    issue_type = Prompt.ask("Issue type (1-4)", default="1")
    issue_map = {"1": "Error/Exception", "2": "Bug/Unexpected behavior", "3": "Performance issue", "4": "Logic error"}
    debug_type = issue_map.get(issue_type, "Error/Exception")

    console.print(f"\n[dim]Paste the error message or describe the issue (Enter + 'END' to finish):[/]")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    error_or_behavior = "\n".join(lines)

    has_code = Confirm.ask("\nDo you have relevant code to share?", default=False)
    code_context = ""
    if has_code:
        console.print("[dim]Paste the code (Enter + 'END' to finish):[/]")
        code_lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            code_lines.append(line)
        code_context = "\n".join(code_lines)

    with console.status("[bold green]Analyzing the issue..."):
        system = """You are an expert debugging assistant.

Analyze this debugging request and provide:

### 1. 🎯 Root Cause Analysis
### 2. 🔍 Step-by-Step Diagnosis
### 3. ✅ Solution & Fix
### 4. 🛡️ Prevention
### 5. 📚 Learning Point

Be specific, practical, and educational."""

        debug_prompt = f"""Issue type: {debug_type}

Error/Issue:
{error_or_behavior}

{"Relevant code:" if code_context else ""}
{code_context if code_context else "No code provided"}"""

        result = ask_groq(system, debug_prompt, max_tokens=2000)

    console.print(Panel(Markdown(result), title="[cyan]🔧 Debug Analysis[/]", expand=False))
    save_to_history("debug", error_or_behavior, result)

# ─── MODE 4: SMART COMMIT MESSAGE ────────────────────────────────────────────
def mode_commit():
    """Generate smart commit messages."""
    console.print("[yellow]📝 Commit Message Generator[/]\n")

    has_diff = Confirm.ask("Do you have a git diff to paste?", default=False)

    if has_diff:
        console.print("[dim]Paste your git diff (Enter + 'END' to finish):[/]")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        changes = "\n".join(lines)
    else:
        changes = Prompt.ask("Describe your changes")

    commit_type = Prompt.ask(
        "Commit type",
        choices=["auto", "feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"],
        default="auto"
    )

    with console.status("[bold green]Generating commit messages..."):
        type_hint = f"\nPreferred type: {commit_type}" if commit_type != "auto" else ""
        system = f"""You are an expert at writing git commit messages following Conventional Commits format.

Format: <type>(scope): <description>
Rules:
- First line max 72 characters
- Use imperative mood ("add" not "added")
- Be specific and professional{type_hint}

Provide exactly 3 options:
### Option 1: Quick (one-liner)
### Option 2: Standard (subject + body)
### Option 3: Detailed (comprehensive)"""

        result = ask_groq(system, f"Write commit messages for:\n\n{changes}", max_tokens=800)

    console.print(Panel(Markdown(result), title="[cyan]Commit Messages[/]", expand=False))
    save_to_history("commit", changes, result)

# ─── MODE 5: SMART Q&A ───────────────────────────────────────────────────────
def mode_ask():
    """Developer Q&A with context building."""
    console.print("[yellow]❓ Developer Q&A Mode[/]\n")

    question = Prompt.ask("Your question")

    has_context = Confirm.ask("\nAdd context (error, tech stack, what you tried)?", default=False)
    full_q = question

    if has_context:
        tech_stack = Prompt.ask("Tech stack (optional, press Enter to skip)", default="")
        has_error = Confirm.ask("Do you have an error message?", default=False)
        error_msg = ""
        if has_error:
            console.print("[dim]Paste error message (Enter + 'END' to finish):[/]")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            error_msg = "\n".join(lines)

        if tech_stack:
            full_q += f"\n\nTech: {tech_stack}"
        if error_msg:
            full_q += f"\n\nError: {error_msg}"

    with console.status("[bold green]Thinking through your question..."):
        system = """You are a helpful senior developer with 10+ years experience.

Structure your answer:
1. **Direct Answer** (2-3 sentences)
2. **Example** (working code if relevant)
3. **Why It Works** (underlying concept)
4. **Common Mistakes**
5. **Next Steps**

Be practical and encouraging."""
        result = ask_groq(system, full_q, max_tokens=1500)

    console.print(Panel(Markdown(result), title="[cyan]Answer[/]", expand=False))

    while Confirm.ask("\nHave a follow-up question?", default=False):
        followup = Prompt.ask("Follow-up")
        conversation = f"Original: {full_q}\n\nPrevious answer: {result}\n\nFollow-up: {followup}"
        with console.status("[bold green]Thinking..."):
            followup_result = ask_groq(system, conversation, max_tokens=1200)
        console.print(Panel(Markdown(followup_result), title="[cyan]Follow-up Answer[/]", expand=False))
        result = followup_result

    save_to_history("ask", question, result)

# ─── MODE 6: EMAIL WRITER ────────────────────────────────────────────────────
def mode_email():
    """Draft professional work emails."""
    console.print("[yellow]📧 Professional Email Writer[/]\n")

    templates = {
        "1": "Custom",
        "2": "Leave Request",
        "3": "Task Status Update",
        "4": "Request Help/Clarification",
        "5": "Meeting Follow-up",
        "6": "Deadline Extension",
        "7": "Bug Report",
        "8": "Feature Proposal",
        "9": "Thank You"
    }

    console.print("Email templates:")
    for k, v in templates.items():
        console.print(f"  {k}. {v}")

    template_choice = Prompt.ask("Choose template (1-9)", default="1")
    template = templates.get(template_choice, "Custom")

    if template == "Custom":
        situation = Prompt.ask("What's the email about?")
    else:
        details = Prompt.ask(f"Details for {template} (optional)", default="")
        situation = f"{template}: {details}" if details else template

    recipient = Prompt.ask(
        "Recipient",
        choices=["Manager", "Senior Developer", "Team", "HR", "Client", "Colleague"],
        default="Manager"
    )
    tone = Prompt.ask(
        "Tone",
        choices=["Friendly & Professional", "Formal", "Urgent", "Apologetic"],
        default="Friendly & Professional"
    )

    extra = Prompt.ask("Additional details (optional)", default="")

    prompt = f"Email type: {situation}\nRecipient: {recipient}\nTone: {tone}"
    if extra:
        prompt += f"\nAdditional details: {extra}"

    with console.status("[bold green]Drafting your email..."):
        system = """You are an expert at writing professional workplace emails for software teams.
Write a complete, ready-to-send email with Subject, Greeting, Body, and Sign-off.
Keep body under 150 words. Use [Your Name] as placeholder."""
        result = ask_groq(system, prompt, max_tokens=700)

    console.print(Panel(Markdown(result), title="[cyan]Your email draft[/]", expand=False))

    console.print("\n[dim]📧 Email tips:[/]")
    console.print("  • Replace [Your Name] with your actual name")
    console.print("  • Read once and adjust tone to your style")
    console.print("  • Check for typos before sending")

    save_to_history("email", situation, result)

# ─── MODE 7: CODE COMPARISON ─────────────────────────────────────────────────
def mode_compare():
    """Compare two code snippets or files."""
    console.print("[yellow]Code comparison mode[/]\n")

    method = Prompt.ask(
        "Input method",
        choices=["files", "paste"],
        default="files"
    )

    if method == "files":
        file1 = Prompt.ask("Path to first file")
        file2 = Prompt.ask("Path to second file")

        if not os.path.exists(file1) or not os.path.exists(file2):
            console.print("[red]One or both files not found[/]")
            return

        with open(file1) as f:
            code1 = f.read()
        with open(file2) as f:
            code2 = f.read()

        lang1 = detect_language(file1)
        lang2 = detect_language(file2)
    else:
        console.print("\n[dim]Paste first code snippet (Enter + 'END' to finish):[/]")
        lines1 = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines1.append(line)
        code1 = "\n".join(lines1)

        console.print("\n[dim]Paste second code snippet (Enter + 'END' to finish):[/]")
        lines2 = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines2.append(line)
        code2 = "\n".join(lines2)

        lang1 = lang2 = "text"

    lang_context = ""
    if lang1 == lang2:
        lang_context = f"Both snippets are in {LANGUAGE_NAMES.get(lang1, lang1)}. "
    else:
        lang_context = f"Code 1 is in {LANGUAGE_NAMES.get(lang1, lang1)}, Code 2 is in {LANGUAGE_NAMES.get(lang2, lang2)}. "

    system = f"""{lang_context}You are an expert code reviewer comparing two code implementations.

Analyze both snippets and provide:

1. **Functional Differences**
2. **Quality Comparison**
3. **Performance**
4. **Language-specific considerations**
5. **Recommendation**

Be specific with code examples."""

    with console.status("[bold green]Comparing code snippets..."):
        result = ask_groq(
            system,
            f"Compare these two implementations:\n\n**Code 1:**\n{code1}\n\n**Code 2:**\n{code2}",
            max_tokens=1500
        )

    console.print(Panel(Markdown(result), title="[cyan]Code Comparison[/]", expand=False))
    save_to_history("compare", "code comparison", result)

# ─── MODE 8: VIEW HISTORY ────────────────────────────────────────────────────
def mode_history():
    """Show command history."""
    history = load_history()

    if not history:
        console.print("[yellow]No history yet. Start using the assistant to build history![/]")
        return

    console.print(f"\n[cyan]Last {len(history)} commands:[/]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Time", width=16)
    table.add_column("Mode", width=12)
    table.add_column("Input", width=40)

    for idx, entry in enumerate(history[-10:], 1):
        time = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M")
        table.add_row(
            str(idx),
            time,
            entry['mode'],
            entry['input'][:40] + ("..." if len(entry['input']) > 40 else "")
        )

    console.print(table)
    console.print()

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    console.print(Panel(
        "[bold cyan]Dev Daily Assistant v4.0[/] — Universal Language Edition\n"
        "[dim]50+ languages | AI code generation | Smart debugging[/]\n"
        "[dim]explain | generate | debug | commit | ask | email | compare | history[/]",
        expand=False
    ))

    if len(sys.argv) < 2:
        console.print("\n[bold]Available modes:[/]\n")

        tree = Tree("🛠️ Commands", style="bold cyan")

        explain_branch = tree.add("📖 [bold]explain[/] [dim]<file>[/] — Understand code (50+ languages)")
        explain_branch.add("Add [bold]--deep[/] for thorough analysis")

        tree.add("⚡ [bold]generate[/] — AI code generation in any language")
        tree.add("🔧 [bold]debug[/] — Smart debugging assistant")
        tree.add("📝 [bold]commit[/] — Generate smart commit messages")
        tree.add("❓ [bold]ask[/] — Dev Q&A with context building")
        tree.add("📧 [bold]email[/] — Draft professional emails")
        tree.add("🔄 [bold]compare[/] — Compare two code snippets")
        tree.add("📜 [bold]history[/] — View your command history")

        console.print(tree)

        console.print("\n[dim]Examples:[/]")
        console.print("  python assistant.py explain app.py")
        console.print("  python assistant.py explain app.rs --deep")
        console.print("  python assistant.py generate")
        console.print("  python assistant.py debug")
        console.print("  python assistant.py compare")

        console.print("\n[cyan]Supported: Python, JS, TS, Java, C++, Go, Rust, PHP, Ruby, Swift, Kotlin, and 40+ more![/]")
        return

    mode = sys.argv[1].lower()

    if mode == "explain":
        if len(sys.argv) < 3:
            console.print("[red]Provide a file:[/] python assistant.py explain <file>")
            console.print("[dim]Add --deep for thorough analysis[/]")
            return
        filepath = sys.argv[2]
        deep = "--deep" in sys.argv
        mode_explain(filepath, deep)

    elif mode == "generate":
        mode_generate()

    elif mode == "debug":
        mode_debug()

    elif mode == "commit":
        mode_commit()

    elif mode == "ask":
        mode_ask()

    elif mode == "email":
        mode_email()

    elif mode == "compare":
        mode_compare()

    elif mode == "history":
        mode_history()

    else:
        console.print(f"[red]Unknown mode:[/] {mode}")
        console.print("Use: explain | generate | debug | commit | ask | email | compare | history")

if __name__ == "__main__":
    main()