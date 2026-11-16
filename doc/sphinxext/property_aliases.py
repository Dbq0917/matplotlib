"""
Sphinx directive to auto-generate the renamed-properties table.

The table is built from the ``_renamed_properties`` dicts defined on
`.Artist` subclasses, so it never needs manual maintenance: registering a
new alias in the source is enough to make it appear in the documentation.
"""

from docutils.parsers.rst import Directive

# Import the modules defining Artist subclasses so that all of them are
# registered before we walk the class hierarchy.
import matplotlib.artist  # noqa: F401
import matplotlib.axes  # noqa: F401
import matplotlib.collections  # noqa: F401
import matplotlib.figure  # noqa: F401
import matplotlib.image  # noqa: F401
import matplotlib.legend  # noqa: F401
import matplotlib.lines  # noqa: F401
import matplotlib.patches  # noqa: F401
import matplotlib.table  # noqa: F401
import matplotlib.text  # noqa: F401
from matplotlib.artist import Artist


def _all_artist_subclasses():
    seen = set()
    stack = [Artist]
    while stack:
        cls = stack.pop()
        if cls in seen:
            continue
        seen.add(cls)
        stack.extend(cls.__subclasses__())
        yield cls


class RenamedPropertiesDirective(Directive):
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        self.state.document.settings.env.note_dependency(__file__)
        rows = []
        for cls in _all_artist_subclasses():
            for old_name, new_name in sorted(
                    vars(cls).get("_renamed_properties", {}).items()):
                rows.append((f"{cls.__module__}.{cls.__name__}",
                             old_name, new_name))
        rows.sort()
        lines = [
            '.. list-table::',
            '   :header-rows: 1',
            '',
            '   * - Class',
            '     - Historical name',
            '     - Current name',
        ]
        for cls_name, old_name, new_name in rows:
            lines += [
                f'   * - ``{cls_name}``',
                f'     - ``{old_name}``',
                f'     - ``{new_name}``',
            ]
        if not rows:
            lines.append('   * - *(none defined)*')
        self.state_machine.insert_input(lines, 'renamed properties table')
        return []


def setup(app):
    app.add_directive("mpl-renamed-properties", RenamedPropertiesDirective)
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
