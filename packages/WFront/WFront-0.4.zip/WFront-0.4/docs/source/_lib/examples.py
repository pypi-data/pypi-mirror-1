# Derived from doctest's ``include`` directive, by David Goodger &
# Dethe Elza.  Original work is in the public domain.
# Thank you David and Dethe.

import os
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst import Directive, directives, states


class DelimitedInclude(Directive):
    """Include a chunk of another file between matching text delimiters.

    Similar to the ``include`` directive, however
    ``delimited-include`` picks text between matching delimiters in
    the text.  Furthermore, the delimiter is supplied to the directive
    in two parts: an id, and a string-format template for composing
    delimiters.  The default format is ``## %s ##``.

    The primary and possibly only advantage of this directive over
    ``include`` is that ``delimited-include`` can include chunks from
    the same file that is being processed.  This allows docstrings to
    include snippets of the code being documented.

    ::
      .\. delimited-include:: examples.py
          :delim-id: 1
          :delim-format: ## %s ##

    And here, in this very ``.py`` file we have::

      The delimiter below is not included, nor is this line or any
      prior line.

      ## 1 ##
      But everything between these delimiters is included.
      ## 1 ##

      The final delimiter, this line and the lines following are not
      included.

    """
    # directly derived from doctools Include
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'literal': directives.flag,
                   'encoding': directives.encoding,
                   'delim-id': directives.unchanged_required,
                   'delim-format': directives.unchanged_required}

    standard_include_path = os.path.join(os.path.dirname(states.__file__),
                                         'include')

    def _load(self):
        # directly derived from doctools Include
        if not self.state.document.settings.file_insertion_enabled:
            raise self.warning('"%s" directive disabled.' % self.name)

        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)
        source_dir = os.path.dirname(os.path.abspath(source))
        path = directives.path(self.arguments[0])
        if path.startswith('<') and path.endswith('>'):
            path = os.path.join(self.standard_include_path, path[1:-1])
        path = os.path.normpath(os.path.join(source_dir, path))
        path = utils.relative_path(None, path)
        encoding = self.options.get(
            'encoding', self.state.document.settings.input_encoding)
        try:
            self.state.document.settings.record_dependencies.add(path)
            include_file = io.FileInput(
                source_path=path, encoding=encoding,
                error_handler=(self.state.document.settings.\
                               input_encoding_error_handler),
                handle_io_errors=None)
        except IOError, error:
            raise self.severe('Problems with "%s" directive path:\n%s: %s.'
                              % (self.name, error.__class__.__name__, error))
        try:
            return include_file.read(), path
        except UnicodeError, error:
            raise self.severe(
                'Problem with "%s" directive:\n%s: %s'
                % (self.name, error.__class__.__name__, error))

    def _process(self, include_text, path):
        # directly derived from doctools Include
        if self.options.has_key('literal'):
            literal_block = nodes.literal_block(include_text, include_text,
                                                source=path)
            literal_block.line = 1
            return [literal_block]
        else:
            include_lines = statemachine.string2lines(include_text,
                                                      convert_whitespace=1)
            self.state_machine.insert_input(include_lines, path)
            return []

    def run(self):
        """Include a section of a file as part of the content of this file."""
        text, path = self._load()
        marker_format = self.options.get('delim-format', '## %s ##')
        marker = marker_format % self.options.get('delim-id')

        start, end = text.find(marker), text.rfind(marker)
        if start == -1 or start == end:
            raise self.severe(
                'Problem with "id" option of "%s" directive:\n'
                'Text "%s" not found.' % (self.name, marker))

        text = text[start + len(marker):end]
        return self._process(text, path)


def setup(app):
    app.add_directive('delimited-include', DelimitedInclude, 1, (1, 0, 1))
