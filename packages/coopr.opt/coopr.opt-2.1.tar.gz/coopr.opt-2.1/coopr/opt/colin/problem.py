#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

"""
Utilities to support the definition of optimization applications that
can be optimized with the Acro COLIN optimizers.
"""

import re
import xml.dom.minidom
import sys
from pyutilib.enum import Enum
from pyutilib.misc import tostr, get_xml_text


response_enum = Enum("FunctionValue", "FunctionValues", "Gradient", "NonlinearConstraintValues", "Jacobian")

class MixedIntVars(object):
  """
  A class that defines a commonly used domain type.
  """

  def __init__(self, node=None):
      self.reals = []
      self.ints = []
      self.bits = []
      if node is not None:
         self.process(node)

  def display(self):
      print "Reals",
      for val in self.reals:
        print val,
      print ""
      print "Integers",
      for val in self.ints:
        print val,
      print ""
      print "Binary",
      for val in self.bits:
        print val,
      print ""

  def process(self,node):
      for child in node.childNodes:
        if child.nodeType == node.ELEMENT_NODE:
            child_text = get_xml_text(child)
            if child_text == "":
              continue
            if child.nodeName == "Real":
              for val in re.split('[\t ]+',child_text):
                self.reals.append(1.0*eval(val))
            elif child.nodeName == "Integer":
              for val in re.split('[\t ]+',child_text):
                self.ints.append(eval(val))
            elif child.nodeName == "Binary":
              for val in child_text:
                if val == '1':
                   self.bits.append(1)
                elif val == '0':
                   self.bits.append(0)



class OptProblem(object):
    """
    A class that defines an application that can be optimized
    by a COLIN optimizer via system calls.
    """

    def __init__(self):
        """
        The constructor.  Derived classes should define the response types.

        By default, only function evaluations are supported in an OptProblem
        instance.
        """
        self.response_types = [response_enum.FunctionValue]


    def main(self, argv):
        """
        The main routine for parsing the command-line and executing
        the evaluation.
        """
        if len(argv) < 3:
            print argv[0 ]+ " <input> <output> <log>"
            sys.exit(1)
        #
        # Get enum strings
        #
        self.response_str = map(str,self.response_types)
        #
        # Parse XML input file
        #
        input_doc = xml.dom.minidom.parse(argv[1])
        point = self.create_point(input_doc.getElementsByTagName("Domain")[0])
        self.validate(point)
        requests = self._handleRequests(input_doc.getElementsByTagName("Requests")[0])
        #
        # Create output XML object
        #
        output_doc = self._process(point,requests)
        OUTPUT = open(sys.argv[2],"w")
        output_doc.writexml(OUTPUT," "," ","\n","UTF-8")
        OUTPUT.close()


    def create_point(self, node):
        """
        Create a point given an XML node with the domain info.

        By default, this generates a MixedIntVars class object, but
        this method could be over-written to customized an OptProblem
        for other search domains.
        """
        return MixedIntVars(node)


    def function_value(self, point):
        """
        Compute a function value.
        """
        return None

    def function_values(self, point):
        """
        Compute a list of function values.
        """
        return []

    def gradient(self, point):
        """
        Compute a function gradient.
        """
        return []

    def nonlinear_constraint_values(self, point):
        """
        Compute nonlinear constraint values.
        """
        return []

    def jacobian(self, point):
        """
        Compute the Jacobian.
        """
        return []


    def _compute_response(self, point, requests):
        """
        Iterate through the requested responses and compute them.
        """
        response = {}
        for key in requests.keys():
            if key not in self.response_str:
                continue
            #
            if key == "FunctionValue":
               response[key] = str(self.function_value(point))
            elif key == "FunctionValues":
               response[key] = tostr(self.function_values(point))
            elif key == "Gradient":
               response[key] = tostr(self.gradient(point))
            elif key == "NonlinearConstraintValues":
               response[key] = tostr(self.nonlinear_constraint_values(point))
            elif key == "Jacobian":
               response[key] = tostr(self.jacobian(point))
            #
        return response


    def _process(self, point, requests):
        """
        Process the XML document
        """
        #
        # Compute response info
        #
        response = self._compute_response(point,requests)
        #
        # Setup document
        #
        doc = xml.dom.minidom.Document()
        root = doc.createElement("ColinResponse")
        doc.appendChild(root)
        for key in requests.keys():
            if key in response.keys():
                elt = doc.createElement(str(key))
                root.appendChild(elt)
                text_elt = doc.createTextNode( response[key] )
                elt.appendChild(text_elt)
            else:
                elt = doc.createElement(str(key))
                root.appendChild(elt)
                text_elt = doc.createTextNode( "ERROR: Unsupported application request "+str(key) )
                elt.appendChild(text_elt)
        return doc


    def _handleRequests(self, node):
        """
        A function that processes the requests
        """
        requests = {}
        for child in node.childNodes:
            if child.nodeType == node.ELEMENT_NODE:
                tmp = {}
                for (name,value) in child.attributes.items():
                    tmp[name]=value
                requests[str(child.nodeName)] = tmp
        return requests

    def validate(self, point):
        """
        This function should throw an exception if an error occurs
        """
        pass



class MixedIntOptProblem(OptProblem):

    def __init__(self):
        OptProblem.__init__(self)
        self.int_lower=[]
        self.int_upper=[]
        self.real_lower=[]
        self.real_upper=[]
        self.nreal=0
        self.nint=0
        self.nbinary=0
        
    def validate(self, point):
        if len(point.reals) !=  self.nreal:
            raise ValueError, "Number of reals is "+str(len(point.reals))+" but this problem is configured for "+str(self.nreal)
        if len(point.ints) !=  self.nint:
            raise ValueError, "Number of integers is "+str(len(point.ints))+" but this problem is configured for "+str(self.nint)
        if len(point.bits) !=  self.nbinary:
            raise ValueError, "Number of binaries is "+str(len(point.bits))+" but this problem is configured for "+str(self.nbinary)
        if len(self.int_lower) > 0:
            for i in range(0,self.nreal):
                if self.int_lower[i] is not None and self.int_lower[i] > point.ints[i]:
                    raise ValueError, "Integer "+str(i)+" has a value "+str(point.ints[i])+" that is lower than the integer lower bound "+str(self.int_lower[i])
                if self.int_upper[i] is not None and self.int_upper[i] < point.ints[i]:
                    raise ValueError, "Integer "+str(i)+" has a value "+str(point.ints[i])+" that is higher than the integer upper bound "+str(self.int_upper[i])

        if len(self.real_lower) > 0:
            for i in range(0,self.nreal):
                if self.real_lower[i] is not None and self.real_lower[i] > point.reals[i]:
                    raise ValueError, "Real "+str(i)+" has a value "+str(point.reals[i])+" that is lower than the real lower bound "+str(self.real_lower[i])
                if self.real_upper[i] is not None and self.real_upper[i] < point.reals[i]:
                    raise ValueError, "Real "+str(i)+" has a value "+str(point.reals[i])+" that is higher than the real upper bound "+str(self.real_upper[i])


        
