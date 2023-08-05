#!/usr/bin/env python

"Prepare the application images."

import os, shutil
import sys, cmdsyntax

# Set definitions.

CRYSTAL_SVG = "crystalsvg"
CRYSTAL_CLEAR = "CrystalClear/kde-icons-crystalclear-0.0.20050623"
TANGO = "tango-icon-theme-0.7.1"

# Icon set texts.

icon_set_texts = {
    CRYSTAL_SVG : """Everaldo's "Crystal SVG" icon theme for KDE
  - see COPYING-CrystalSVG.txt for copyright and licensing information""",
    CRYSTAL_CLEAR : """Everaldo's "Crystal Clear" icon theme for KDE
  - see COPYING-CrystalClear.txt for copyright and licensing information from
    the Debian repackaging of that work""",
    TANGO : """Tango Icon Theme
  - see COPYING-Tango.txt and AUTHORS-Tango.txt for copyright and licensing
    information from the original source package"""
    }

# Icon definitions.

icon_sets = {
    CRYSTAL_SVG : [
        ("actions", "kontact_contacts", "card"),
        ("actions", "viewmag", "search"),
        ("actions", "kontact_journal", "journal"),
        ("actions", "kontact_mail", "message"),
        ("actions", "kontact_todo", "to-do"),
        ("actions", "kontact_date", "event"),
        ("actions", "down", "sort-ascending"),
        ("actions", "up", "sort-descending"),
        ("actions", "filenew", "created"),
        ("apps", "clock", "appointment"),
        ("actions", "redo", "continued"),
        ("filesystems", "folder", None)
        ],
    CRYSTAL_CLEAR : [
        ("mimetypes", "vcard", "card"),
        #("actions", "edit", None),
        ("actions", "viewmag", "search"),
        ("actions", "easymoblog", "journal"),
        ("apps", "email", "message"),
        #("apps", "reminders", "to-do"),
        ("apps", "korganizer", "to-do"),
        ("apps", "cal", "event"),
        ("actions", "down", "sort-ascending"),
        ("actions", "up", "sort-descending"),
        ("mimetypes", "empty", "created"),
        ("apps", "xclock", "appointment"),
        ("actions", "redo", "continued"),
        ("filesystems", "folder", None)
        ],
    TANGO : [
        #("apps", "system-users", "card"),
        ("mimetypes", "x-office-address-book", "card"),
        ("actions", "system-search", "search"),
        ("apps", "accessories-text-editor", "journal"),
        ("apps", "internet-mail", "message"),
        ("apps", "accessories-text-editor", "to-do"),
        ("mimetypes", "x-office-calendar", "event"),
        ("actions", "go-down", "sort-ascending"),
        ("actions", "go-up", "sort-descending"),
        ("actions", "document-new", "created"),
        ("actions", "appointment", None),
        ("actions", "go-jump", "continued"),
        ("places", "folder", None)
        ]
    }

# Patch definitions.

patches = {
    CRYSTAL_SVG : [],
    CRYSTAL_CLEAR : [],
    TANGO : [
        ("tango-appointment-new.svg.diff", "actions", "appointment-new", "appointment")
        ]
    }

# Recommended sizes.

recommended_sizes = {
    CRYSTAL_SVG : ["32x32", "22x22", "16x16"],
    CRYSTAL_CLEAR : ["32x32", "22x22", "16x16", "48x48", "64x64", "128x128"],
    TANGO : ["32x32", "scalable"]
    }

if __name__ == "__main__":

    # Get the icon location.

    syntax = cmdsyntax.Syntax("""
        --copy
        [ --icon-set=SET ]
        [ --icon-base=BASE_DIR ]
        [ --icon-size=SIZE ]
        [ --convert ]
        """)

    syntax_matches = syntax.get_args(sys.argv[1:])

    try:
        args = syntax_matches[0]
    except IndexError:
        print syntax.syntax
        print "Icon sets defined so far are:"
        for icon_set in icon_sets.keys():
            print icon_set, recommended_sizes[icon_set]
        sys.exit(1)

    icon_set = args.get("icon-set", CRYSTAL_CLEAR)
    icon_base = args.get("icon-base", "/home/paulb/Software/Graphical")
    icon_size = args.get("icon-size", "32x32")

    print "Using icon set", icon_set
    print "Looking for icons in", icon_base
    print "Size set to", icon_size

    icons_dir = os.path.join(icon_base, icon_set)
    if not os.path.exists(icons_dir):
        print "Icons directory not found:", icons_dir
        sys.exit(1)

    # Find out where the package distribution directory is.

    program = sys.argv[0]
    cwd = os.path.split(program)[0]
    parts = os.path.split(cwd)
    if parts[-1] == "tools":
        parts = parts[:-1]
    base = os.path.join(*parts)

    # Set up the environment and find the application resource directory.

    applications = os.path.join(base, "applications")
    webcalendar_images = os.path.join(applications, "WebCalendar", "Resources", "images")
    if not os.path.exists(webcalendar_images):
        print "Making", webcalendar_images
        os.mkdir(webcalendar_images)

    # Find the patches directory.

    patches_dir = os.path.join(base, "tools", "patches")

    # Determine the correct directories, along with filename extensions.

    if icon_size == "scalable":
        icon_ext = "svg"
        target_ext = "svg"
        icon_size_collection = icon_size
    else:
        if args.has_key("convert"):
            icon_ext = "svg"
            width, height = icon_size.split("x")
            icon_size_collection = "scalable"
        else:
            icon_ext = "png"
            icon_size_collection = icon_size
        target_ext = "png"

    # Write a note about the icons to the images directory.

    f = open(os.path.join(webcalendar_images, "ICONS.txt"), "w")
    try:
        f.write("Icons provided by the icon set described as follows:\n\n")
        f.write(icon_set_texts[icon_set] + "\n")

        # Apply any patches to the icons.

        if icon_size_collection == "scalable":
            f.write("\nImage patch details:\n\n")

            for patch_name, section, icon, new_icon in patches[icon_set]:
                icon_filename = os.path.join(icon_size_collection, section, icon) + os.path.extsep + icon_ext
                new_icon_filename = os.path.join(icon_size_collection, section, new_icon) + os.path.extsep + icon_ext
                patch = os.path.join(patches_dir, patch_name)
                image = os.path.join(icons_dir, icon_filename)
                new_image = os.path.join(icons_dir, new_icon_filename)
                os.system("patch -o %s %s %s" % (new_image, image, patch))
                f.write("Image %s patched to produce %s.\n" % (icon_filename, new_icon_filename))

        # Copy the icons.

        f.write("\nImage details:\n\n")

        for section, icon, target in icon_sets[icon_set]:
            icon_filename = os.path.join(icon_size_collection, section, icon) + os.path.extsep + icon_ext
            new_icon_filename = (target or icon) + os.path.extsep + target_ext
            image = os.path.join(icons_dir, icon_filename)
            target_image = os.path.join(webcalendar_images, new_icon_filename)
            # NOTE: The conversion depends on ksvgtopng from the kdelibs-bin package (or
            # NOTE: equivalent).
            if args.has_key("convert"):
                cmd = "ksvgtopng %s %s %s %s" % (width, height, image, target_image)
                os.system(cmd)
            else:
                shutil.copy(image, target_image)
            f.write("Image %s copied to produce %s.\n" % (icon_filename, new_icon_filename))

    finally:
        f.close()

# vim: tabstop=4 expandtab shiftwidth=4
