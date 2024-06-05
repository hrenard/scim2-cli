import click
import httpx
from click import ClickException
from scim2_client import SCIMClientError
from scim2_models import Message
from scim2_models import Resource
from sphinx_click.rst_to_ansi_formatter import make_rst_to_ansi_formatter

from .utils import DOC_URL
from .utils import formatted_payload
from .utils import split_headers


@click.command(cls=make_rst_to_ansi_formatter(DOC_URL), name="delete")
@click.argument("resource-type", required=True)
@click.argument("id", required=True)
@click.option(
    "-h", "--headers", multiple=True, help="Header to pass in the HTTP requests."
)
@click.option(
    "--indent/--no-indent",
    is_flag=True,
    default=True,
    help="Indent JSON response payloads.",
)
@click.pass_context
def delete_cli(ctx, resource_type, id, headers, indent):
    """Perform a `SCIM DELETE query <https://www.rfc-editor.org/rfc/rfc7644#section-3.6>`_ request.

    .. code-block:: bash

        scim https://scim.example delete user 1234
    """

    try:
        resource_type = ctx.obj["resource_types"][resource_type]
    except KeyError:
        ok_values = ", ".join(ctx.obj["resource_types"])
        raise ClickException(
            f"Unknown resource type '{resource_type}'. Available values are: {ok_values}'"
        )

    try:
        response = ctx.obj["client"].delete(
            resource_type, id, headers=split_headers(headers)
        )

    except (httpx.HTTPError, SCIMClientError) as exc:
        raise ClickException(exc) from exc

    if response:
        payload = (
            response.model_dump()
            if isinstance(response, (Resource, Message))
            else response
        )
        payload = formatted_payload(payload, indent)
        click.echo(payload)
