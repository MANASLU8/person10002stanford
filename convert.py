import sys, os, re
from file_operations import read
from nltk.tokenize import RegexpTokenizer

INPUT_FOLDERS = sys.argv[1:] if len(sys.argv) > 1 else ['data3', 'data5']
OUTPUT_FILE = 'corpus.txt'
NOT_ENTITY_MARK = 'O'
FORBIDDEN_FILES = ['list']
SEPARATOR = ' '

TOKEN_PATTERN = '\w+|[\d]+|[!@#$%^&*().?":{}|<>\'"/]'
TAG_MAPPING = {'LOC': 'Location', 'PER': 'Person', 'MEDIA': 'Org', 'GEOPOLIT': 'LocOrg', 'ORG': 'Org'}

def read_lines(filename):
    with open(filename) as f:
        return [line.replace('\n', '') for line in f.readlines()]

def write_lines(filename, lines):
    with open(filename, "w") as f:
        f.write('\n'.join(lines))

def lines2entities(lines):
    entities = []
    for line in lines:
        first_char_id = line.split('\t')[1].split(' ')[1]
        last_char_id = line.split('\t')[1].split(' ')[2]
        entity_id = line.split('\t')[1].split(' ')[0]
        entities.append({'first_char_id': int(first_char_id), 'last_char_id': int(last_char_id), 'tag': entity_id})
    return entities

def get_entity(current_char_id, entities):
    for entity in entities:
        if entity['first_char_id'] <= current_char_id and entity['last_char_id'] > current_char_id:
            return entity['tag']
    return 'O'

if __name__ == "__main__":
    tokenizer = RegexpTokenizer(TOKEN_PATTERN, gaps=False)
    # Get unique input file names without extensions
    output_lines = []
    tags = set()
    for folder in sorted(INPUT_FOLDERS):
        input_files = set()
        for r, d, f in os.walk(folder):
            for file in f:
                if file.split('.')[0] not in FORBIDDEN_FILES:
                    input_files.add(file.split('.')[0])

        #print(input_files)

        
        for input_file_name in sorted(input_files):
            # Read text
            text_file_name = f'{folder}/{input_file_name}.txt'
            text = read(text_file_name, line_sep = '  ')
            tokens = tokenizer.tokenize(text)
            gaps = re.split(TOKEN_PATTERN, text)[1:]

            # Read entities
            ann_file_name = f'{folder}/{input_file_name}.ann'
            lines = read_lines(ann_file_name)
            entities = lines2entities(lines)

            offset = 0
            for i in range(len(tokens)):
                token = tokens[i]
                # Gap after the token
                gap_length = len(gaps[i])
                # Length of the token
                token_length = len(token)
                #print(f'{offset} {token}')

                entity = TAG_MAPPING.get(get_entity(offset, entities), NOT_ENTITY_MARK)
                #tags.add(entity)
                output_lines.append(f'{token}{SEPARATOR}{entity}')

                offset += (gap_length + token_length)

    #print(tags)
    write_lines(OUTPUT_FILE, output_lines)