ZebraID Program V2 — Natural Biography, External TXT
====================================================

This version is designed to read like the example:

"I'm Julian. I live over in Denver, Colorado, where I work as an urban planner..."

The program generates a natural first-person fictional biography that can be
placed before another prompt.

IMPORTANT:
main.py does NOT contain the biography source data.

All source data is stored in:
ZebraID_V2_Natural_Data.txt


FILES
-----

main.py
ZebraID_V2_Natural_Data.txt
test_v2.py
README.txt


DATA STORED IN THE TXT FILE
---------------------------

100 biography templates
100 first names
100 locations
100 career profiles
100 relationship descriptions
100 weekend activities
100 pet descriptions
100 hobbies
100 food preferences


CAREER DATA IS LINKED
---------------------

Career records use:

JOB | EDUCATION | CAREER REASON

Example:

urban planner | city and regional planning |
getting to help shape the local community is pretty much my dream job

The program selects the entire record together. This makes the story more
realistic because the job and education stay related.


HOW TO RUN ON WINDOWS
---------------------

1. Download the ZIP.
2. Right-click it and choose Extract All.
3. Open the extracted folder.
4. Click the File Explorer address bar.
5. Type:

cmd

6. Press Enter.


GENERATE ONE BIOGRAPHY
----------------------

python main.py


GENERATE 10
-----------

python main.py --count 10


PUT THE BIOGRAPHY BEFORE A PROMPT
---------------------------------

python main.py --prompt "What career change should I consider?"


TEST EVERYTHING
---------------

No extra packages are required.

python -m unittest -v test_v2.py


WHAT THE TESTS CHECK
--------------------

1. Every data section in the TXT file has exactly 100 entries.
2. All placeholders are replaced.
3. The result is a long first-person biography.
4. 100 calls produce varying biographies.
5. Completely restarting Python does not restart the same sequence.
6. A supplied prompt is printed after the generated biography.


RANDOMNESS
----------

The program uses secrets.choice() for random selections.
No fixed seed is used.
