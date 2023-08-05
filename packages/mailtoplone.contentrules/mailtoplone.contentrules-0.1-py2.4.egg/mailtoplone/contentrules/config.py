# -*- coding: utf-8 -*-
#
# File: config.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__    = """Hans-Peter Locher<hans-peter.locher@inquant.de>"""
__docformat__ = 'plaintext'

# EmailHeader Condition
# Vocabulary for Header fields according to rfc 2822, rfc2045, rfc2183
vo_headers = ("From",
              "Sender",
              "Reply-To",
              "To",
              "Cc",
              "Bcc",
              "Message-ID",
              "In-Reply-To",
              "References",
              "Subject",
              "Comments",
              "Keywords",
              "Resent-Date",
              "Resent-From",
              "Resent-Sender",
              "Resent-To",
              "Resent-Cc",
              "Resent-Bcc",
              "Resent-Message-ID",
              "Return-Path",
              "Received",
              "Mime-Version",
              "Content-Type",
              "Content-Transfer-Encoding",
              "Content-ID",
              "Content-Description",
              "Content-Disposition",
              )

vo_headers_default = "Subject"

# vim: set ft=python ts=4 sw=4 expandtab :
