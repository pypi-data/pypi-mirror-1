import os
from nose.plugins.base import Plugin

import elementtree.ElementTree as ET
import traceback
import datetime

class NoseXML(Plugin):
	"""
	NoseXML is a plugin providing an XML report output for nosetests.

	Dependencies: nose, elementtree

	Installation:

		From easy_install:
		easy_install nosexml

		From the package directory:
		sudo python ./setup.py install
	
	Usage:

		nosetests --with-nosexml --xml-report-file=my_report.xml
	
	Example output:

		<tests>
			<meta>
				<datetime>2006-08-14 14:37:37.679480</datetime>
			</meta>
			
			<test status="skipped" id="package.module.class.function" />
			
			<test status="success" id="package.module.class.function">
				<capture>1+1=2</capture>
			</test>

			<test status="failure" id="package.module.class.function">
				<capture />
				<error>AssertionFailure</error>
				<traceback>
					<frame file="/home/richard/testproject/foo.py" line="100" function="callTest">
						test("fish")
					</frame>
					<frame file="/home/richard/testproject/foo.py" line="120" function="test">
						Assert True == False
					</frame>
				</traceback>
			</test>

			<test status="error" id="package.module.class.function">
				<capture>Who knows what generates one of these?</capture>
			</test>

			<test status="deprecated" id="package.module.class.function" />
		</tests>
	"""
	def add_options(self, parser, env=os.environ):
		Plugin.add_options(self, parser, env)
		parser.add_option("--xml-report-file", action="store", default="nose_report.xml", dest="report_file", help="File to output XML report to")
	
	def configure(self, options, config):
		Plugin.configure(self, options, config)
		self.conf = config
		self.reportFile = options.report_file
	
	def begin(self):
		""" Set up root, begin tree like this:

		<tests>
			<meta>
				<datetime>2006-08-14 14:37:37.679480</datetime>
			</meta>
		</tests>
		"""
		self.root = ET.Element("tests")
		metaElement = ET.SubElement(self.root, "meta")
		ET.SubElement(metaElement, "datetime").text = str(datetime.datetime.now())

	def finalize(self, result):
		""" Write out report as serialized XML """
		tree = ET.ElementTree(self.root)
		tree.write(self.reportFile)
	
	def addSkip(self, test):
		"""
		Skipped this test
			
		<test status="skipped" id="package.module.class.function" />
		"""
		e = ET.SubElement(self.root, "test")
		e.set("status", "skipped")
		e.set("id", test.id())
	
	def addSuccess(self, test, capture):
		"""
		Test was successful
		
		<test status="success" id="package.module.class.function">
			<capture>1+1=2</capture>
		</test>
		"""
		e = ET.SubElement(self.root, "test")
		e.set("status", "success")
		e.set("id", test.id())
		ET.SubElement(e, "capture").text=capture
	
	def addFailure(self, test, error, capture, tb):
		"""
		Test failed
		
		<test status="failure" id="package.module.class.function">
			<capture />
			<error>AssertionFailure</error>
			<traceback>
				<frame file="/home/richard/testproject/foo.py" line="100" function="callTest">
					test("fish")
				</frame>
				<frame file="/home/richard/testproject/foo.py" line="120" function="test">
					Assert True == False
				</frame>
			</traceback>
		</test>
		"""
		e = ET.SubElement(self.root, "test")
		e.set("status", "failure")
		e.set("id", test.id())
		ET.SubElement(e, "capture").capture = capture
		ET.SubElement(e, "error").text = ''.join(traceback.format_exception_only(error[0], error[1]))
		tracebackElement = ET.SubElement(e, "traceback")
		for (fname, line, func, text)  in traceback.extract_tb(error[2]):
			frameElement = ET.SubElement(tracebackElement, "frame")
			frameElement.set("file", fname)
			frameElement.set("line", str(line))
			frameElement.set("function", str(func))
			frameElement.text = text

	def addError(self, test, capture):
		"""
		Test errored. Not sure what causes this
		
		<test status="error" id="package.module.class.function">
			<capture>Who knows what generates one of these?</capture>
		</test>
		"""
		e = ET.SubElement(self.root, "test")
		e.set("status", "error")
		e.set("id", test.id())
		ET.SubElement(e, "capture").text = capture
	
	def addDeprecated(self, test):
		"""
		Test is deprecated

		<test status="deprecated" id="package.module.class.function" />
		"""
		e = ET.SubElement(self.root, "test")
		e.set("status", "deprecated")
		e.set("id", test.id())
