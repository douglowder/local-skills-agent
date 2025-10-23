# test_generator Skill

## Purpose
Generate skeleton unit tests for Python modules using the **`analyze_code`** skill as a foundation.  The skill automatically extracts public functions and classes from a target module, then produces a corresponding `test_<module>.py` file containing basic `pytest` test functions.

## Prerequisites
- The **`analyze_code`** skill is available in the skills repository.
- The target Python file resides in the project root or a sub‑directory.
- `pytest` is installed in the environment where the tests will be executed.

## Usage
```bash
python -m skill_runner test_generator <path/to/module.py>
```
The skill will:
1. Run `analyze_code` on the supplied module.
2. Create a test file named `test_<module>.py` in the same directory as the module.
3. For each public function, generate a `test_<function_name>()` placeholder.
4. For each class, generate a `Test<ClassName>` test class with a placeholder test method.
5. Add helpful comments guiding the developer on how to flesh out the tests.

## Implementation Steps
1. **Read the target file** – Ensure the path is valid and read the contents.
2. **Invoke `analyze_code`** – Pass the file path to obtain a JSON description of functions and classes.
3. **Parse the analysis** – Extract public symbols (exclude dunder methods, private helpers).
4. **Generate test code** – Build a string containing the test file contents:
   - Import the module under test.
   - For each function: create a test stub.
   - For each class: create a test class with a placeholder method.
5. **Write the test file** – Save the generated string to `test_<module>.py`.
6. **Return success message** – Provide the path to the created test file.

## Sample Output (for a module `math_utils.py`)
```python
# test_math_utils.py
import math_utils


def test_add():
    """TODO: Implement test for math_utils.add"""
    pass


def test_multiply():
    """TODO: Implement test for math_utils.multiply"""
    pass
```

## Edge Cases & Error Handling
- If the module contains no public functions or classes, the skill should still create an empty test file with a comment indicating that no public API was found.
- If the target file does not exist or is not a valid Python file, the skill should return an error message.
- If `analyze_code` fails, propagate the error message.

## Skill Template Structure
```markdown
# test_generator Skill

## Purpose
...

## Prerequisites
...

## Usage
...

## Implementation Steps
...

## Sample Output
...

## Edge Cases & Error Handling
...
```

Feel free to adapt or extend this template to suit the project conventions.