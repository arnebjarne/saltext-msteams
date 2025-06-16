"""
Module for sending messages to MS Teams

.. versionadded:: 2017.7.0

:configuration: This module can be used by either passing a hook_url
    directly or by specifying it in a configuration profile in the salt
    master/minion config. For example:

.. code-block:: yaml

    msteams:
      hook_url: https://outlook.office.com/webhook/837
"""

import logging

import salt.utils.json
from salt.exceptions import SaltInvocationError

log = logging.getLogger(__name__)

__virtualname__ = "msteams"


def __virtual__():
    """
    Return virtual name of the module.
    :return: The virtual name of the module.
    """
    return __virtualname__


def _get_hook_url():
    """
    Return hook_url from minion/master config file
    or from pillar
    """
    hook_url = __salt__["config.get"]("msteams.hook_url") or __salt__["config.get"](
        "msteams:hook_url"
    )

    if not hook_url:
        raise SaltInvocationError("No MS Teams hook_url found.")

    return hook_url


def post_card(message, hook_url=None, title=None, theme_color=None):
    """
    Send a message to an MS Teams channel.
    :param message:     The message to send to the MS Teams channel.
    :param hook_url:    The Teams webhook URL, if not specified in the configuration.
    :param title:       Optional title for the posted card
    :param theme_color:  Optional hex color highlight for the posted card
    :return:            Boolean if message was sent successfully.

    CLI Example:

    .. code-block:: bash

        salt '*' msteams.post_card message="Build is done"
    """

    if not hook_url:
        hook_url = _get_hook_url()

    if not message:
        log.error("message is a required option.")

    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "msteams": {"width": "Full"},
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": title,
                            "color": theme_color,
                            "weight": "bolder",
                            "size": "large",
                            "wrap": True,
                        },
                        {"type": "CodeBlock", "codeSnippet": message, "language": "PlainText"},
                    ],
                },
            }
        ],
    }

    headers = {
        "Content-Type": "application/json",
    }

    result = salt.utils.http.query(
        hook_url,
        method="POST",
        header_dict=headers,
        data=salt.utils.json.dumps(payload),
        status=True,
    )

    if result["status"] <= 202:
        return True
    else:
        return {"res": False, "message": result.get("body", result["status"])}
