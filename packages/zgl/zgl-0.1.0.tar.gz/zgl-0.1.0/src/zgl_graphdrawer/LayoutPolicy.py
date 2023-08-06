import logging
import os
import re
import subprocess
import tempfile

import numpy

class GraphVizLayoutPolicy(object):

    def __init__(self, contextManager):
        self._manager = contextManager
        return

    def temporaryFilePath(self, value=None):
        if value is not None:
            self._tmpFile = None
            
        if not hasattr(self, '_tmpFile'):
            self._tmpFile = os.sep.join(
                [tempfile.gettempdir(), 'temp_dotFile.dot'])
            
        return self._tmpFile


    def layoutNodes(self, nodes, edges):

        dotFile = "digraph G {\n"

        #for node in nodes:
        #	dotFile += "\t\"%s\"\n" % node.nodeData.name()

        for edge in edges:
            dotFile += "\t\"%s\" -> \"%s\"\n" % (edge.inputNode().nodeData.name(), edge.outputNode().nodeData.name())
        dotFile += "}"

        logging.debug(dotFile)

        # fp = open('temp_dotFile.dot','w')
        tmpFile = self.temporaryFilePath()
        fp = open(tmpFile, 'w')
        fp.write(dotFile)
        fp.close()


        # use the subprocess module to execute
        command = [self._manager.commandPath('dot'),
                   tmpFile]
        processObj = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout = processObj.stdout

        boundingbox = ""
        for line in stdout.readlines():
            logging.debug(line)

            match = re.search('^\s*graph \[(.*)\];$', line)
            if match is not None:
                attributeString = match.group(1)
                logging.debug("Graph has attributes: %s" % match.group(1))
                attributes = self.getAttributesDict(attributeString)
                if attributes.has_key('bb'):
                    bb = map(float, attributes['bb'].split(','))
                continue;

            foundNode = False
            for node in nodes:
                nodeName = "%s" % (node.nodeData.name())
                match = re.search('^\s*"{0,1}'+nodeName+'"{0,1}\s*\[(.*)\];$', line)
                if match is not None:
                    attributeString = match.group(1)
                    attributes = self.getAttributesDict(attributeString)
                    if attributes.has_key('pos'):
                        #(node.x,node.y) = map(float, attributes['pos'].split(','))
                        #node.x = node.x * 1.5
                        #node.y = node.y * 1.5
                        position = 1.5 * numpy.matrix(
                            ' '.join(attributes['pos'].split(',')))
                        logging.debug('position >> %s' % position)
                        node.setPosition(position[0,0], position[0,1])
                        pass
                    if attributes.has_key('width'):
                        (node.width) = float(attributes['width']) * 80
                    if attributes.has_key('height'):
                        (node.height) = float(attributes['height']) * 80
                    foundNode = True;
                if foundNode:
                    break

        return (bb[2],bb[3])

    
    def getAttributesDict(self, attributeString):
        dict = {}
        matches = re.findall('(\w+)="(.*?)"',attributeString)
        if matches is not None:
            for match in matches:
                attributeName = match[0]
                attributeValue = match[1]
                dict[attributeName] = attributeValue
        return dict
