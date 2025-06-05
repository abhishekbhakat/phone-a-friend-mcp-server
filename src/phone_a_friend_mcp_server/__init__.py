import asyncio
import logging
import os
import sys

import click

from phone_a_friend_mcp_server.config import PhoneAFriendConfig
from phone_a_friend_mcp_server.server import serve


@click.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@click.option("--api-key", help="API key for external AI services")
@click.option("--model", help="Model to use (e.g., 'gpt-4', 'anthropic/claude-3.5-sonnet')")
@click.option("--provider", help="Provider type ('openai', 'openrouter', 'anthropic', 'google')")
@click.option("--base-url", help="Base URL for API")
def main(verbose: int, api_key: str = None, model: str = None, provider: str = None, base_url: str = None) -> None:
    """MCP server for Phone-a-Friend AI consultation"""
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)

    # Read environment variables with proper precedence
    config_api_key = (
        api_key
        or os.environ.get("OPENROUTER_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
    )
    config_model = model or os.environ.get("PHONE_A_FRIEND_MODEL")
    config_provider = provider or os.environ.get("PHONE_A_FRIEND_PROVIDER")
    config_base_url = base_url or os.environ.get("PHONE_A_FRIEND_BASE_URL")

    # Initialize configuration
    try:
        config = PhoneAFriendConfig(api_key=config_api_key, model=config_model, provider=config_provider, base_url=config_base_url)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)

    # Start the server
    asyncio.run(serve(config))


if __name__ == "__main__":
    main()
