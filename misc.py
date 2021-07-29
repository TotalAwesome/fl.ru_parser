import requests
import re

html = requests.get("https://www.fl.ru/projects/")
text = html.text.splitlines()

def parse_match(matches):
    result = []
    for m in matches:
        new_matches = re.findall("\[(\d+),'([^']*)'", m)
        result.extend(new_matches)
    result.sort(key=lambda x: int(x[0]))
    result = {k: v for (k, v) in result}
    return result


for line in text:
    if 'filter_specs[2]' in line:
        matches = re.findall('filter_specs\[\d+\]=([^;]*)', line)
        result = parse_match(matches)
        matches = re.findall('ids\[(\d+)\]=([^;]*)', line)
        specs = {}
        for m in matches:
            specs[m[0]] = sorted(
                re.findall('(\d+):', m[1]),
                key=lambda x: int(x)
            )

        for spec_id in sorted(specs.keys(), key=lambda x: int(x)):
            msg = f'Категория {spec_id}:\n\t'
            lst = []
            for i in specs[spec_id]:
                lst.append(f'{i} : {result.get(i)}')
            msg += '\n\t'.join(lst)
            print(msg)
