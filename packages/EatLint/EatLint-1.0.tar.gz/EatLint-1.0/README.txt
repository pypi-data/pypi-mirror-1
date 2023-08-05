EatLint is a Trac__ plugin that adds a lint report summarizer and a lint chart to
Bitten__.  This means that when a Bitten build that includes a lint step
the output can not only be captured but reported on. The report shows
the number of problems per file by category: convention, refactor,
error, and warning as well as showing the totals for each file, for each
category, and a grand-total showing the state of the entire project.
Similarly the chart plugin charts the total number of problems as well
as individual lines for each category. This gives you an idea of the
readability of your project's code over time.

__ http://trac.edgewall.org
__ http://bitten.edgewall.org

EatLint's code and templates are based on the code and templates provided by the Bitten project for coverage and unittest data.  The Bitten code and templates are provided under a BSD-style license and so is this plugin.  Please see [License] for a copy of the license.

Example:

An example build recipe might like this:

<build xmlns:python="http://bitten.cmlenz.net/tools/python"
	xmlns:svn="http://bitten.cmlenz.net/tools/svn"
	xmlns:sh="http://bitten.cmlenz.net/tools/sh">
	      
    <step id="checkout" description="Checkout source">
	<svn:checkout path="${path}" url="http://echospiral.com/svn/eatlint" revision="${revision}"/>
    </step>

    <step id="lint" description="Gather lint report">
	<sh:exec executable="pylint" args="eatlint -f parseable" output="pylint.out"/>
	<python:pylint file="pylint.out"/>
    </step>

</build>

Installation:

Installation is done just as for any other Trac plugin.  Using the
easy_install command from setuptools is the easiest (provided you have
already setuptools installed):

easy_install eatlint

After that you must configure your Trac project to use the plugin.  Edit
conf/trac.ini in your Trac directory to include this:

[components]
eatlint.* = enabled
