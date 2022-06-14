# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import datetime

import sgtk
from sgtk import TankError
from tank.util import sgre as re
from tank_vendor import six
from tank_vendor.shotgun_api3 import sg_timezone

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_globals",
)


def get_hyperlink_html(url, name):
    """
    Provides an html string for a hyperlink pointing to the given URL
    and displaying the provided string name.

    :param str url: The URL that the hyperlink navigates to.
    :param str name: The string name to display.

    :return: HTML string.
    """
    # Older versions of core don't have the SG_LINK_COLOR constant, so we'll
    # just fall back on SG_FOREGROUND_COLOR in that case.
    color = sgtk.platform.constants.SG_STYLESHEET_CONSTANTS.get(
        "SG_LINK_COLOR",
        sgtk.platform.constants.SG_STYLESHEET_CONSTANTS["SG_FOREGROUND_COLOR"],
    )

    html = "<a href='%s' style='text-decoration: none; color: %s'><b>%s</b></a>" % (
        url,
        color,
        name,
    )

    return html


def resolve_sg_fields(token_str):
    """
    Returns the sg fields for all tokens given a token_str.

    :param token_str: String with tokens, e.g. "{code}_{created_by}"
    :returns: All shotgun fields, e.g. ["code", "created_by"]
    """

    fields = []

    for token in resolve_tokens(token_str):
        fields.extend(token["sg_fields"])

    return fields


def convert_token_string(token_str, sg_data):
    """
    Convert a string with {tokens} given a shotgun data dict

    :param token_str: Token string as defined in the shotgun fields hook
    :param sg_data: Data dictionary to get values from
    :returns: string with tokens replaced with actual values
    """

    if not token_str:
        return ""

    for token in resolve_tokens(token_str):
        sg_field = None
        sg_value = None
        i = 0
        while sg_field is None and i < len(token["sg_fields"]):
            field = token["sg_fields"][i]
            if field in sg_data:
                sg_value = sg_data[field]
                sg_field = field
            i += 1

        # if sg_field is None or sg_value is None or sg_value == []:
        if sg_field is None or not sg_value:
            # None of the token sg_fields were found in the sg_data. Check whether or not to
            # display an "empty" or default text.
            if token["pre_roll"] or token["post_roll"]:
                # For tokens with pre or post rolls, just display an empty string.
                resolved_value = ""
            else:
                # Use the last fallback field to display an "empty" phrase.
                if len(token["sg_fields"]) > 0:
                    sg_field = token["sg_fields"][-1]

                if not sg_field:
                    resolved_value = ""
                else:
                    if is_valid_entity_type_field(sg_data["type"], sg_field):
                        resolved_value = shotgun_globals.get_empty_phrase(
                            sg_data["type"], sg_field
                        )
                    else:
                        # The 'sg_field' is just fallback text to display.
                        resolved_value = sg_field

        else:
            resolved_value = sg_field_to_str(
                sg_data["type"], sg_field, sg_value, token["directives"]
            )

            # Add pre and post rolles
            if token["pre_roll"]:
                resolved_value = "{pre_roll}{value}".format(
                    pre_roll=token["pre_roll"],
                    value=resolved_value,
                )
            if token["post_roll"]:
                resolved_value = "{value}{post_roll}".format(
                    value=resolved_value,
                    post_roll=token["post_roll"],
                )

        # Replace the token with the value
        token_str = token_str.replace("{%s}" % token["full_token"], resolved_value)

    return token_str


def resolve_tokens(token_str):
    """
    Resolve a list of tokens from a string.

    Tokens are on the following form:

        {[preroll]shotgun.field.name|sg_field_name_fallback::directive[postroll]}

    Basic Examples:

    - {code}                         # simple format
    - {sg_sequence.Sequence.code}    # deep links
    - {artist|created_by}            # if artist is null, use creted_by

    Directives are also supported - these are used by the formatting logic
    and include the following:

    - {sg_sequence::showtype}        # will generate a link saying
                                     # 'Sequence ABC123' instead of just
                                     # 'ABC123' like it does by default
    - {sg_sequence::nolink}          # no url link will be created

    Optional pre/post roll - if a value is null, pre- and post-strings are
    omitted from the final result. Examples of this syntax:

    - {[Name: ]code}                 # If code is set, 'Name: xxx' will be
                                     # printed out, otherwise nothing.
    - {[Name: ]code[<br>]}           # Same but with a post line break

    :param token_str: String with tokens, e.g. "{code}_{created_by}"
    :returns: a list of tuples with (full_token, sg_fields, directive, preroll, postroll)
    """

    if not token_str:
        return []

    try:
        # find all field names ["xx", "yy", "zz.xx"] from "{xx}_{yy}_{zz.xx}"
        raw_tokens = set(re.findall(r"{([^}^{]*)}", token_str))
    except Exception as error:
        raise TankError("Could not parse '%s' - Error: %s" % (token_str, error))

    fields = []
    for raw_token in raw_tokens:

        pre_roll = None
        post_roll = None
        directives = None

        processed_token = raw_token

        match = re.match(r"^\[([^\]]+)\]", processed_token)
        if match:
            pre_roll = match.group(1)
            # remove preroll part from main token
            processed_token = processed_token[len(pre_roll) + 2 :]

        match = re.match(r".*\[([^\]]+)\]$", processed_token)
        if match:
            post_roll = match.group(1)
            # remove preroll part from main token
            processed_token = processed_token[: -(len(post_roll) + 2)]

        if "::" in processed_token:
            # we have a special formatting directive
            # e.g. created_at::ago
            # (sg_field_str, directive) = processed_token.split("::")
            sg_field_and_directives = processed_token.split("::")
            sg_field_str = sg_field_and_directives[0]
            directives = sg_field_and_directives[1:]
        else:
            sg_field_str = processed_token

        if "|" in sg_field_str:
            # there is more than one sg field, we have a
            # series of fallbacks
            sg_fields = sg_field_str.split("|")
        else:
            sg_fields = [sg_field_str]

        fields.append(
            {
                "full_token": raw_token,
                "sg_fields": sg_fields,
                "directives": directives,
                "pre_roll": pre_roll,
                "post_roll": post_roll,
            }
        )

    return fields


def sg_field_to_str(sg_type, sg_field, value, directive=None):
    """
    Converts a Shotgun field value to a string.

    Formatting directives can be passed to alter the conversion behaviour:

    Entity Dictionary directives:
        - showtype: Show the type for links, e.g. return "Shot ABC123" instead
        of just "ABC123"

        - nolink: don't return a <a href> style hyperlink for links, instead just
        return a string.

        - typeonly: Show only the type for hte links

    Timestamp directives ('created_at', 'updated_at'):
        - short_timestamp: Display a shorter timestamp, e.g. 1h, 1d, 1w, etc.

    Status directives ('sg_status_list'):
        - text: Display the status name as is
        - displaytext: Display the user friendly status
        - icon: Display the icon

    Version Number directives ('version_number'):
        - zeropadded: Pad the version number with up to three zeros
        - A format string that contains a single argument specifier to substitute the
          version number integer value; e.g. '%03d' will achieve the same as 'zeropadded'.

    :param sg_type: Shotgun data type
    :param sg_field: Shotgun field name
    :param value: value to turn into a string
    :param directive: Formatting directive, see above
    :returns: The Shotgun field formatted as a string
    """

    str_val = None

    if value is None:
        return shotgun_globals.get_empty_phrase(sg_type, sg_field)

    # Allow multiple directives
    directives = directive or []
    if isinstance(directives, six.string_types):
        directives = [directives]

    # Get the relative field from deep links; e.g. published_file_type.PublishedFileType.sg_status_list
    # will get the 'sg_status_list' as the relative field. This is to ensure that the correct formatting
    # is applied to deeply linked fields.
    relative_sg_field = sg_field.split(".")[-1]
    sg_field_names = set((sg_field, relative_sg_field))

    if isinstance(value, dict) and set(["type", "id", "name"]) == set(value.keys()):
        # entity link
        if "showtype" in directives:
            # links are displayed as "Shot ABC123"

            # get the nice name from our schema
            # this is so that it says "Level" instead of "CustomEntity013"
            entity_type_display_name = shotgun_globals.get_type_display_name(
                value["type"]
            )
            link_name = "%s %s" % (entity_type_display_name, value["name"])
        else:
            # links are just "ABC123"
            link_name = value["name"]

        if "nolink" in directives:
            str_val = link_name
        else:
            str_val = get_hyperlink_html(
                url="sgtk:%s:%s" % (value["type"], value["id"]),
                name=link_name,
            )

        if "typeonly" in directives:
            str_val = shotgun_globals.get_type_display_name(value["type"])

    elif isinstance(value, list):
        # list of items
        link_urls = []
        for list_item in value:
            link_urls.append(sg_field_to_str(sg_type, sg_field, list_item, directive))
        str_val = ", ".join(link_urls)

    elif sg_field_names & set(("created_at", "updated_at")):
        timestamp_format = directives[0] if directives else None
        (str_val, _) = create_human_readable_timestamp(value, timestamp_format)

    elif "sg_status_list" in sg_field_names:
        if not directives:
            # No directives given, default to show the icon and display text (in that order).
            directives = ["icon", "displaytext"]

        # Go through the directives and build the status string in order of the given directives
        # e.g. the default directives, ["icon", "dispalytext"], will display the status icon and
        # then the user friendly status name ("In Progress" instead of "ip").
        str_vals = []
        for d in directives:
            if d == "text":
                str_vals.append(value)
            elif d == "displaytext":
                str_vals.append(shotgun_globals.get_status_display_name(value))
            elif d == "icon":
                color_str = shotgun_globals.get_status_color(value)
                if color_str:
                    str_vals.append(
                        "<span style='color: rgb(%s)'>" "&#9608;</span>" % color_str
                    )
            else:
                assert False, "Unknown directive for 'sg_status_list' field"

        str_val = " ".join(str_vals)

    elif "version_number" in sg_field_names:
        if directives:
            if "zeropadded" in directives:
                str_format = "%03d"
            else:
                str_format = directives[0]

            str_val = str_format % value

    # elif sg_field == "type":
    elif "type" in sg_field_names:
        if "showtype" in directives:
            str_val = shotgun_globals.get_type_display_name(value)

    if str_val is None:
        str_val = str(value)
        # make sure it gets formatted correctly in html
        str_val = str_val.replace("\n", "<br>")

    return str_val


def is_valid_entity_type_field(sg_type, sg_field):
    """
    Return True if the given Shotgun entity type and field are valid by checking if a schema
    can be found for them.

    :param sg_type: Shotgun data type.
    :param sg_field: Shotgun field name.
    :return: True if valid else False.
    :rtype: bool
    """

    try:
        shotgun_globals.get_data_type(sg_type, sg_field)
        # A schema was found, indicating a valid Shotgun type and field.
        is_valid = True
    except ValueError:
        # Schema could not be found for the given Shotgun type and field.
        is_valid = False

    return is_valid


def create_human_readable_timestamp(datetime_value, timestamp_format):
    """
    Formats a time stamp the way dates are formatted in the
    Shotgun activity stream. Examples of output:

    Recent posts: 10:32
    This year: 24 June 10:32
    Last year and earlier: 12 December 2007

    :param datetime_value: The datetime value to format
    :type datetime_obj: datetime.datetime | float
    :param timestamp_format: Formatting hint
    :type timestamp_format: str; supported types:
        'short_timestamp': e.g. 1h, 1d, 1w, 1mo, 1yr
    :returns: date str
    """

    if datetime_value is None:
        return "No timestamp", ""

    if isinstance(datetime_value, datetime.datetime):
        datetime_obj = datetime_value

    elif isinstance(datetime_value, float):
        datetime_obj = datetime.datetime.fromtimestamp(
            datetime_value, tz=sg_timezone.LocalTimezone()
        )
    else:
        # Unsupported datetime value type
        raise TankError(
            "Could not parse datetime value of type '{type}'".format(
                type=type(datetime_value).__name__
            )
        )

    # standard format
    full_time_str = datetime_obj.strftime("%a %d %b %Y %H:%M")
    now = datetime.datetime.now(sg_timezone.LocalTimezone())

    if datetime_obj > now:
        # future times are reported precisely
        return full_time_str, full_time_str

    # get the delta and components
    delta = now - datetime_obj

    # the timedelta structure does not have all units; bigger units are converted
    # into given smaller ones (hours -> seconds, minutes -> seconds, weeks > days, ...)
    # but we need all units:
    delta_years = delta.days // 365
    delta_weeks = delta.days // 7
    delta_days = delta.days
    delta_hours = delta.seconds // (60 * 60)
    delta_minutes = delta.seconds // 60
    short_format = timestamp_format == "short_timestamp"

    if delta_years > 0:
        # more than one year ago
        if short_format:
            time_str = "{years}y".format(years=delta_years)
        else:
            # e.g. 26 June 2012
            time_str = datetime_obj.strftime("%d %b %Y %H:%M")

    elif delta_weeks > 0:
        # more than one week agao
        if short_format:
            time_str = "{weeks}w".format(weeks=delta_weeks)
        else:
            # e.g. 26 June
            time_str = datetime_obj.strftime("%d %b %H:%M")

    elif delta_days > 0:
        # more than one day ago
        if short_format:
            time_str = "{days}d".format(days=delta_days)
        else:
            # e.g. 26 June
            time_str = datetime_obj.strftime("%d %b %H:%M")

    elif delta_hours > 0:
        # today more than an hour agao
        if short_format:
            time_str = "{hours}h".format(hours=delta_hours)
        else:
            # e.g. 23:22
            time_str = datetime_obj.strftime("%H:%M")

    elif delta_minutes > 0:
        # today more than a minute ago
        if short_format:
            time_str = "{mins}m".format(mins=delta_minutes)
        else:
            # e.g. 23:22
            time_str = datetime_obj.strftime("%H:%M")
    else:
        # today within seconds ago
        if short_format:
            time_str = "{seconds}s".format(seconds=delta.seconds)
        else:
            # e.g. 23:22
            time_str = datetime_obj.strftime("%H:%M")

    return time_str, full_time_str
