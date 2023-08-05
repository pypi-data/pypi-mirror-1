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

	Optional: --xml-accumulate will open and insert additional test results into an already existing xml file. The intention is to allow multiple independent runs of nosetest to create a single report.

Example output:

	<testset>
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
	</testset>
"""

