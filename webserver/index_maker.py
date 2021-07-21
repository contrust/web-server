import os


def make_index(index_path: str, root: str) -> None:
    index, directory_path = get_path_last_element(index_path), get_dir_from_path(index_path)
    relative_path = directory_path.replace(root, "")
    with open(index_path, mode='w') as page:
        page.write('<!DOCTYPE html>\n'
                   '<html lang="en">\n'
                   '<head>\n'
                   f'<title>Index of {relative_path}</title>\n'
                   '</head>\n'
                   '<body>\n'
                   f'<h1>Index of {relative_path}</h1><hr><pre>')
        if relative_path != os.path.sep:
            page.write('<a href="../">../</a>\n')
        for directory in map(get_path_last_element, filter(os.path.isdir, get_directory_list(directory_path))):
            page.write(f'<a href="{directory}/">{directory}/</a>\n')
        for file in map(get_path_last_element, filter(os.path.isfile, get_directory_list(directory_path))):
            if file != index:
                page.write(f'<a href="{file}">{file}</a>\n')
        page.write('</pre><hr>\n'
                   '</body>\n'
                   '</html>')


def get_directory_list(directory_path: str) -> iter:
    return map(lambda x: f'{directory_path}{x}', os.listdir(directory_path))


def get_path_last_element(path: str) -> str:
    return path[path.rfind(os.path.sep) + 1:]

def get_dir_from_path(path: str) -> str:
    return path[:path.rfind(os.path.sep) + 1]
