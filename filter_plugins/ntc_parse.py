#!usr/bin/env python

HAS_NTC_TEMPLATES = True
try:
    from ntc_templates.parse import _get_template_dir as ntc_get_template_dir
except:
    HAS_NTC_TEMPLATES = False

HAS_TEXTFSM = True
try:
    from clitable import CliTableError
    import clitable
except:
    try:
        from textfsm.clitable import CliTableError
        import textfsm.clitable as clitable
    except:
        HAS_TEXTFSM = False

if HAS_NTC_TEMPLATES:
    NTC_TEMPLATES_DIR = ntc_get_template_dir()
else:
    NTC_TEMPLATES_DIR = 'ntc_templates/templates'


def clitable_to_dict(cli_table):
    """Converts TextFSM cli_table object to list of dictionaries
    """
    objs = []
    for row in cli_table:
        temp_dict = {}
        for index, element in enumerate(row):
            temp_dict[cli_table.header[index].lower()] = element
        objs.append(temp_dict)

    return objs


def get_structured_data(output, command, platform, index_file, template_dir):
    cli_table = clitable.CliTable(index_file, template_dir)

    attrs = dict(
        Command=command,
        Platform=platform
    )
    try:
        cli_table.ParseCmd(output, attrs)
        structured_data = clitable_to_dict(cli_table)
    except CliTableError:
        # Invalid or Missing template
        # rather than fail, fallback to return raw text
        structured_data = [output]

    return structured_data


def ntc_parse(output, command, platform, template_dir="./ntc-templates/templates", index_file="index"):
    structured_data_response_list = []
    structured_data = {}
    if isinstance(output, dict):
        for device, command_output in output.items():
            raw_txt = command_output[command]
            sd = get_structured_data(raw_txt)
            temp = dict(device=device, response=sd)
            structured_data_response_list.append(temp)
    else:
        structured_data = get_structured_data(output, command, platform, index_file, template_dir)
    return structured_data or structured_data_response_list


class FilterModule(object):
    ''' A filter to split a string into a list. '''
    def filters(self):
        return {
            'ntc_parse': ntc_parse
        }
