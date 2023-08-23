import pathlib
import csv
from typing import List

import configparser

# config version
version = 1

"""options = {
    "configversion":{"default":version, "required":True, "description":"Config version"},
    "file":{"required":False, "description":"ROM location"},
    "directory":{"required":True, "description":"Project Directory"},
    "projectname":{"default":"No name", "required":True, "description":"Project Name"},
    "projectdescription":{"default":"No description", "description":"Project Description"},
    "projectversion":{"default": "0", "description":"Project Version"},
    "projectrom":{"description":"Default Output ROM Location"}
}"""

sections = ["location", "project"]
options = {
    "location": ["directory"],
    "project": ["name", "description", "version", "output"],
}

defaults = {'origin_nds_fn': 'base.nds'}
home_dir: pathlib.Path = pathlib.Path.home().joinpath('.ppre2')
home_dir.mkdir(exist_ok=True)


def qtSetter(s, o, v, meta):
    meta[s+"_"+o+"_value"].setText(v)


def qtGetter(s, o, meta):
    return str(meta[s+"_"+o+"_value"].text())


def load(f, setter, meta=None):
    parser = configparser.ConfigParser()
    parser.readfp(f)
    for s in sections:
        for o in options[s]:
            setter(s, o, parser.get(s, o), meta)


def write(f, getter, meta=None):
    parser = configparser.ConfigParser()
    parser.add_section("config")
    parser.set("config", "version", str(version))
    for s in sections:
        parser.add_section(s)
        for o in options[s]:
            parser.set(s, o, getter(s, o, meta))
    parser.write(f)


project = None
mw = None


class OpenedHistoyRecorder:
    """ A fixed capacity opened folder history recorder using LRU algorithm """

    limit = 6

    def __init__(self) -> None:
        self.his = {}
        self.his_file = home_dir.joinpath('opened_history')

        if self.his_file.exists():
            with open(self.his_file) as fr:
                for ln in csv.reader(fr):
                    self.his[ln[0]] = int(ln[1])

    def push(self, record: str):
        for k in self.his:
            if k != record:
                self.his[k] += 1
            else:
                self.his[k] = 0

        self.his[record] = 0

        if len(self.his) > OpenedHistoyRecorder.limit:
           k, _ = max(self.his.items(), key=lambda x: x[1])

           self.his.pop(k)

    def fetch(self) -> List[str]:
        return list(map(lambda x: x[0], sorted(self.his.items(), key=lambda x: x[1])))

    def drop(self, k: str):
        self.his.pop(k)

    def save(self):
        # newline = '' it's important for windows python
        with open(self.his_file, 'w', newline='') as fw:
            csv.writer(fw).writerows(self.his.items())



if __name__ == "__main__":
    recorder = OpenedHistoyRecorder()
    recorder.save()


