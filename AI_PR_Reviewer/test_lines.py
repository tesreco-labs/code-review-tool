from change_parser import extract_changes

patch = """
@@ -10,3 +10,4 @@

-if x == None:
+if x is None:

+print("Done")
"""

changes = extract_changes(patch)

for change in changes:

    print()

    print(change)