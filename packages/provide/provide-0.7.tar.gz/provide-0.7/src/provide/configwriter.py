import re

class ConfigWriter(object):

    def updateLines(self, configLines, updateLines):
        updateDoc = ConfigDoc(updateLines)
        configDoc = ConfigDoc(configLines)
        configDoc.update(updateDoc)
        self.newLines = configDoc.asLines()

    def updateFile(self, configPath, updateLines):
        configFile = open(configPath, 'r')
        configLines = configFile.readlines()
        configFile.close()
        self.updateLines(configLines, updateLines)
        newLines = [l+'\n' for l in self.newLines]
        configFile = open(configPath, 'w')
        configLines = configFile.writelines(newLines)
        configFile.close()


class ConfigDoc(object):

    def __init__(self, lines):
        reSection = re.compile('^\[\w+\]')
        self.sections = []
        self.prelines = []
        section = None
        for line in lines:
            match = reSection.match(line)
            if match:
                if section and section.lines:
                    lastLine = section.lines[-1]
                    if lastLine.name == '' and lastLine.comment == '':
                        section.lines.pop()
                sectionName = match.group()[1:-1]
                section = ConfigSection(sectionName)
                self.sections.append(section)
            elif section:
                section.parseLine(line)
            else:
                self.prelines.append(line.strip())

    def update(self, configDoc):
        sectionDict = {}
        for section in self.sections:
            sectionDict[section.name] = section
        for section in configDoc.sections:
            if section.name in sectionDict:
                sectionDict[section.name].update(section)
            else:
                self.sections.append(section)

    def asLines(self):
        lines = []
        for section in self.sections:
            lines += section.asLines()
            lines.append('')
        self.sections and lines.pop()
        return self.prelines + lines
        

class ConfigSection(object):

    def __init__(self, name):
        self.name = name
        self.lines = []

    def parseLine(self, line):
        self.lines.append(ConfigLine(line))

    def update(self, configSection):
        lineDict = {}
        for line in self.lines:
            if line.name:
                lineDict[line.name] = line
        for line in configSection.lines:
            if line.name in lineDict:
                lineDict[line.name].update(line)
            else:
                self.lines.append(line)

    def asLines(self):
        lines = []
        lines.append('[%s]' % self.name)
        for line in self.lines:
            lines.append(line.asText())
        return lines


class ConfigLine(object):

    def __init__(self, line):
        self.parseLine(line)

    def parseLine(self, line):
        lineSplit = line.split('#')
        nameValueSplit = lineSplit[0].split('=')
        self.name = nameValueSplit[0].strip()
        self.value = '='.join(nameValueSplit[1:]).strip()
        self.comment = '#'.join(lineSplit[1:]).strip()

    def update(self, configLine):
        self.value = configLine.value

    def asText(self):
        text = ""
        if self.name:
            text += "%s = %s" % (self.name, self.value)
        if self.name and self.comment:
            text += "  " 
        if self.comment:
            text += "#%s" % self.comment
        return text

