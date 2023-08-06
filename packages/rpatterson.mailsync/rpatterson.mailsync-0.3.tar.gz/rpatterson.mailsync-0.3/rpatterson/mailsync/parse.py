def add_options(parser, other, title=None, exclude=()):
    parser.set_defaults(**other.defaults)
    if title:
        group = parser.add_option_group(title, other.description)
    else:
        group = parser
    for option in other.option_list:
        if not (option.get_opt_string() in exclude or
                parser.has_option(option.get_opt_string())):
            group.add_option(option)
    for other_group in getattr(other, 'option_groups', ()):
        add_options(parser, other_group, other_group.title)
