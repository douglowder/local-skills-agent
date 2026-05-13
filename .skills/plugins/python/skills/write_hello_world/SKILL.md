---
name: write_hello_world
description: Write a simple Python "Hello, World!" program to hello_world.py in the current directory. Use when the user asks for a hello-world example or wants to verify the write_file tool works.
version: 1.0.0
---

# Write Hello World Skill

Write a simple "Hello, World!" program in Python.

## Instructions

When this skill is invoked, you should:

1. Create a Python file called `hello_world.py` in the current directory
2. The file should contain a simple Python program that prints "Hello, World!"
3. Use the `write_file` tool to create the file
4. After creating the file, confirm to the user that the file was created successfully

## Example Output

The created file should contain:

```python
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```
