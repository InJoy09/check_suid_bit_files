#!/usr/bin/python
# I use Tabs
import subprocess
import json

print('-' * 15)


def check_exist_json_file():
	try:
		open('suid_bit_data.json')
		return True
	except FileNotFoundError:
		return False


def creat_json_file(dict_):
	with open('suid_bit_data.json', 'w') as file:
		json.dump(dict_, file, indent=2)


def get_files_suid_bit():
	stdout_paths = subprocess.run('echo $PATH', shell=True, capture_output=True, text=True).stdout
	paths_lst = stdout_paths.split(':')[:-1]

	files_suid_bit = []
	for path in paths_lst:
		stdout_files_suid_bit = subprocess.run('ls -l ' + path + ' | grep -P ^...[sS]', shell=True, capture_output=True, text=True).stdout
		if stdout_files_suid_bit != '':
			for line in stdout_files_suid_bit.split('\n')[:-1]:
				name_file = line.split()[-1]
				files_suid_bit.append(path + '/' + name_file)
	return files_suid_bit


def get_dict_files_and_hashes():
	files_lst = get_files_suid_bit()
	dict_files_and_hashes = {}
	stderr = []
	for el in files_lst:
		proc = subprocess.run(['sha256sum', el], capture_output=True, text=True)
		if proc.stderr != '':
			stderr.append(proc.stderr)
		if proc.stdout != '':
			hash_file, name_file = proc.stdout.split()
			dict_files_and_hashes[name_file] = hash_file
	[print(el[:-1], 'нужны права root') for el in stderr]
	return dict_files_and_hashes


def compare_hashes(files_and_hashes):
	is_change = False
	with open('suid_bit_data.json') as file:
		previous_hashes = json.load(file)
	duplicate_previous_hashes = previous_hashes.copy()

	current_hashes = files_and_hashes
	new_current_hashes = []

	for key, value in current_hashes.items():
		if key in previous_hashes:
			if value == previous_hashes[key]:
				res = 'ok'
			else:
				res = 'changed'
				is_change = True
			line = 41 - len(key)
			print(key, '.' * line, res, sep='')
			del duplicate_previous_hashes[key]
		else:
			new_current_hashes.append(key)

	print()
	if duplicate_previous_hashes:
		print('В текущем списке по сравнению с предыдущим отсутствуют следующие фалы:')
		[print(el) for el in duplicate_previous_hashes]
		is_change = True
	if new_current_hashes:
		print('Появились новые файлы:')
		[print(el) for el in new_current_hashes]
		is_change = True
	return is_change


def main():
	files_and_hashes = get_dict_files_and_hashes()
	is_exist_file = check_exist_json_file()
	if not is_exist_file:
		creat_json_file(files_and_hashes)
		print('Хэш файлов записан в файл')
		print('При следующих запусках будет происходить проверка данных')
	else:
		if compare_hashes(files_and_hashes):
			if input('\nОбновить данные?(y)>_') == 'y':
				creat_json_file(files_and_hashes)


main()
