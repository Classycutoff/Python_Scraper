import os
import re

novel_path = "d:\Books\Royal_Road\The_Runic_Artist"

readme_regex = "- \*\*(\d+)\. \[(.*)\]\(.*\)\*\*"
with open(os.path.join(novel_path, "README.md"), "r", encoding="utf-8") as f:
    readme_str = f.read()


found_all = re.findall(readme_regex, readme_str)
i, j = zip(*found_all)
print(i, j)


# test_str = "D:\\Books\\Royal_Road\\The_Gate_Traveler\\chapters\\Chapter-37_-Traveling-Merchant/Healer.md"

# print(test_str.replace("/", ""))
