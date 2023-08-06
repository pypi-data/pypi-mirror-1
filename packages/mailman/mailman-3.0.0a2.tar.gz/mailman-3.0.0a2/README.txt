Mailman - The GNU Mailing List Management System
Copyright (C) 1998-2009 by the Free Software Foundation, Inc.

INTRODUCTION

    This is GNU Mailman, a mailing list management system distributed under
    the terms of the GNU General Public License (GPL) version 3 or later.  The
    name of this software is spelled "Mailman" with a leading capital `M' but
    with a lower case second `m'.  Any other spelling is incorrect.

    Mailman is written in Python, a free object-oriented scripting language.
    Python is available for all platforms that Mailman is supported on, which
    includes GNU/Linux and most other Unix-like operating systems
    (e.g. Solaris, *BSD, MacOSX, etc.).  It does not run on Windows, although
    web and mail clients on any platform should be able to interact with
    Mailman just fine.

    Mailman was originally developed by John Viega.  Subsequent development
    (through version 1.0b3) was by Ken Manheimer.  Further work towards the
    1.0 final release was a group effort, with the core contributors being:
    Barry Warsaw, Ken Manheimer, Scott Cotton, Harald Meland, and John Viega.
    Version 1.0 and beyond have been primarily maintained by Barry Warsaw with
    contributions from many; see the ACKNOWLEDGMENTS file for details.  Jeremy
    Hylton helped considerably with the Pipermail code in Mailman 2.0.
    Mailman 2.1 is now being primarily maintained by Mark Sapiro and Tokio
    Kikuchi.  Barry Warsaw is the lead developer on Mailman 3.

    The Mailman home page is:

        http://www.list.org

    with mirrors at:

        http://www.gnu.org/software/mailman
        http://mailman.sf.net

    You might also be interested in the Mailman wiki at:

        http://wiki.list.org

    Mailman 3.0 requires Python 2.6 or greater, which can be downloaded from:

        http://www.python.org


FEATURES

    **Mailman 3.0 is alpha software and some of this information may be out of
      date or not currently working.  This will improve as the alpha releases
      are developed.**

    Mailman has most of the standard features you'd expect in a mailing list
    manager, and more:

    - Web based list administration for nearly all tasks.  Web based
      subscriptions and user configuration management.  A customizable "home
      page" for each mailing list.

    - Privacy features such as moderation, open and closed list subscription
      policies, private membership rosters, and sender-based filters.

    - Automatic web based archiving built-in with support for private and
      public archives, and hooks for external archivers.

    - Per-user configuration optional digest delivery for either
      MIME-compliant or RFC 1153 style "plain text" digests.

    - Integrated mail/Usenet gateways.

    - Integrated auto-replies.

    - Email commands.

    - Integrated bounce detection within an extensible framework.

    - Integrated spam detection, and MIME-based content filtering.

    - An extensible mail delivery pipeline.

    - Support for virtual domains.


REQUIREMENTS

    The default mail delivery mechanism uses a direct SMTP connection to
    whatever mail transport agent you have running on port 25.  You can thus
    use Mailman with any such MTA, however with certain MTAs (e.g. Exim and
    Postfix), Mailman will support thru-the-web creation and removal of
    mailing lists.

    Mailman works with any web server that supports CGI/1.1.  The HTML it
    generates should be friendly to most web browsers and network connections.

    You will need root access on the machine hosting your Mailman installation
    in order to complete some of the configuration steps.  See the INSTALL.txt
    file for details.

    Mailman's web and email user interface should be compatible with just
    about any mail reader or web browser, although a mail reader that is MIME
    aware will be a big help.  You do not need Java, JavaScript, or any other
    fancy plugins.


FOR MORE INFORMATION

    For information on this alpha release, see docs/ALPHA.txt

    More documentation is available in the docs directory, and on-line (see
    below).  Installation instructions are contained in the
    docs/readmes/INSTALL.txt file.  Upgrading information is available in the
    docs/readmes/UPGRADING.txt file.  See the docs/NEWS.txt file for a list of
    changes since version 0.9.

    The online documentation can be found in

        file:admin/www/index.html

    in the directory in which you unpacked Mailman.

    There is an online FAQ maintained by the Mailman community, which contains
    a vast amount of information:

        http://www.python.org/cgi-bin/faqw-mm.py

    There is a wiki for more community-driven information:

        http://wiki.list.org

    The wiki includes the online FAQ maintained by the Mailman community, 
    which contains a vast amount of information:

        http://wiki.list.org/display/DOC/Frequently+Asked+Questions

    As well as links to further documentation:

        http://wiki.list.org/display/DOC/

    There are also several mailing lists that can be used as resources
    to help you get going with Mailman.

    Mailman-Users
        An list for users of Mailman, for posting questions or problems
        related to installation, use, etc.  We'll try to keep the deep
        technical discussions off this list.

        http://mail.python.org/mailman/listinfo/mailman-users

    Mailman-Announce
        A read-only list for release announcements an other important news.

        http://mail.python.org/mailman/listinfo/mailman-announce

    Mailman-Developers
        A list for those of you interested in helping develop Mailman 2's
        future direction.  This list will contain in-depth technical
        discussions.

        http://mail.python.org/mailman/listinfo/mailman-developers

    Mailman-I18N
        A list for the discussion of the Mailman internationalization
        effort.  Mailman 2.1 is fully multi-lingual.

        http://mail.python.org/mailman/listinfo/mailman-i18n

    Mailman-Checkins
        A read-only list which is an adjunct to the public anonymous CVS
        repository.  You can stay on the bleeding edge of Mailman development
        by subscribing to this list.

        http://mail.python.org/mailman/listinfo/mailman-checkins

    The Mailman project is coordinated on SourceForge at

        http://sf.net/projects/mailman

    You should use SourceForge to report bugs and to upload patches.



Local Variables:
mode: indented-text
indent-tabs-mode: nil
End:
