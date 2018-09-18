import os


def calc_size(files):
    if not files:
        return 0
    sizes = []
    for _file in files:
        if isinstance(_file, tuple) or isinstance(_file, list):
            sizes.append(_file[1])
        else:
            sizes.append(os.path.getsize(_file))
    return sum(sizes)


def create_bat_file(files, batfilename):
    with open(batfilename, 'w+') as batfile:
        for _file in files:
            line = '\ndelete %s'
            if isinstance(_file, tuple) or isinstance(_file, list):
                line = line % _file[1]
            else:
                line = line % _file
            batfile.write(line)


def unlink(p):
    if os.path.isfile(p):
        try:
            os.unlink(p)
        except WindowsError as wine:
            print (str(wine))
