"""ntc_parse."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

HAS_NTC_TEMPLATES = True
try:
    from ntc_templates.parse import _get_template_dir as ntc_get_template_dir
except ModuleNotFoundError:
    HAS_NTC_TEMPLATES = False

HAS_TEXTFSM = True
try:
    import clitable
    from clitable import CliTableError
except ModuleNotFoundError:
    try:
        from textfsm import clitable
        from textfsm.clitable import CliTableError
    except ModuleNotFoundError:
        HAS_TEXTFSM = False

if HAS_NTC_TEMPLATES:
    NTC_TEMPLATES_DIR = ntc_get_template_dir()
else:
    NTC_TEMPLATES_DIR = "ntc_templates/templates"


def clitable_to_dict(cli_table):
    """Convert TextFSM cli_table object to list of dictionaries."""
    objs = []
    for row in cli_table:
        temp_dict = {}
        for index, element in enumerate(row):
            temp_dict[cli_table.header[index].lower()] = element
        objs.append(temp_dict)

    return objs


def get_structured_data(
    output, command, platform, index_file, template_dir, data_model
):  # pylint: disable=too-many-arguments
    """Takes output and gets structured data."""
    cli_table = clitable.CliTable(index_file, template_dir)

    attrs = dict(Command=command, Platform=platform)
    try:
        cli_table.ParseCmd(output, attrs)
        if data_model == "textfsm":
            structured_data = clitable_to_dict(cli_table)
        else:
            # Only textfsm is supported right now.
            structured_data = [output]
    except CliTableError:
        # Invalid or Missing template
        # rather than fail, fallback to return raw text
        structured_data = [output]

    return structured_data


def ntc_parse(
    output, command, platform, template_dir=NTC_TEMPLATES_DIR, index_file="index", data_model="textfsm"
):  # pylint: disable=too-many-arguments
    """Parses data and turns it into structured data."""
    structured_data_response_list = []
    structured_data = {}
    if isinstance(output, dict):
        for device, command_output in output.items():
            raw_txt = command_output[command]
            sd = get_structured_data(raw_txt, data_model)
            temp = dict(device=device, response=sd)
            structured_data_response_list.append(temp)
    else:
        structured_data = get_structured_data(output, command, platform, index_file, template_dir, data_model)
    return structured_data or structured_data_response_list


class FilterModule(object):  # pylint: disable=useless-object-inheritance
    """A filter to split a string into a list."""

    def filters(self):
        """Ansible filter."""
        return {"ntc_parse": ntc_parse}
