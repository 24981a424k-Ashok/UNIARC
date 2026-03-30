
import os

# Use a relative path or a more robust absolute path
file_path = os.path.join(os.getcwd(), "web", "templates", "business_intel.html")

if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

tokens = {
    '{{': content.count('{{'),
    '}}': content.count('}}'),
    '{%': content.count('{%'),
    '%}': content.count('%}'),
}

print(f"Token counts for {os.path.basename(file_path)}:")
for token, count in tokens.items():
    print(f"{token}: {count}")

is_balanced = True
if tokens['{{'] != tokens['}}']:
    print(f"ERROR: Unbalanced {{{{ }}}} !! ({tokens['{{']} vs {tokens['}}']})")
    is_balanced = False
if tokens['{%'] != tokens['%}']:
    print(f"ERROR: Unbalanced {{% %}} !! ({tokens['{%']} vs {tokens['%}']})")
    is_balanced = False

if is_balanced:
    print("All Jinja blocks are balanced.")

# Check for splits
lines = content.splitlines()
for i, line in enumerate(lines):
    # Very basic check for split tags
    if '{{' in line and '}}' not in line:
        print(f"SPLIT at line {i+1}: Open '{{{{' but no '}}}}' on same line")
    if '{%' in line and '%}' not in line:
        # Some tags ARE naturally split, but let's see which ones
        if not any(x in line for x in ['{% if', '{% for', '{% elif', '{% else', '{% endif', '{% endfor']):
             print(f"SUSPICIOUS SPLIT at line {i+1}: '{line.strip()}'")
